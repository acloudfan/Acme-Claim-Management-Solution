"""
Image service for image upload/delete operations.
"""
from fastapi import UploadFile
from sqlalchemy.orm import Session
from src.api.models.claim import ClaimImage
from src.api.models.damage import Damage
from src.api.services.base_service import BaseService
from src.api.services.claim_service import ClaimService
from src.api.services.cost_service import CostService
from src.api.ai.damage_detector import get_damage_detector
from src.api.config import settings
from src.api.exceptions import ValidationError, ResourceNotFoundError
from src.api.constants import ClaimAction, ActorType, ClaimState
from src.api.services.event_logger import log_event
import shutil
from pathlib import Path
from datetime import datetime
import math

class ImageService(BaseService):
    """Service for image upload/delete operations"""

    def __init__(self, db: Session):
        super().__init__(db)
        # Root directory for all claim images
        self.images_root = Path(settings.IMAGES_ROOT_FOLDER)
        self.images_root.mkdir(exist_ok=True)

    @staticmethod
    def round_labor_hours(hours: float) -> float:
        """
        Round labor hours UP to nearest 0.5 increment.

        Industry standard: Labor is billed in 0.5 hour increments.

        Examples:
            0.1 → 0.5
            1.2 → 1.5
            2.0 → 2.0
            2.3 → 2.5
            3.7 → 4.0

        Args:
            hours: Raw labor hours (can be any float)

        Returns:
            Rounded labor hours (always in 0.5 increments)
        """
        return math.ceil(hours * 2) / 2

    def _validate_image_file(self, file: UploadFile):
        """Validate image file type and size"""
        # Check filename exists
        if not file.filename:
            raise ValidationError("Filename is required")

        # Check file extension
        ext = file.filename.split('.')[-1].lower()
        if ext not in settings.ALLOWED_IMAGE_TYPES:
            raise ValidationError(
                f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
            )

        # Check file size (read in chunks to avoid memory issues)
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if size > max_size:
            raise ValidationError(
                f"File too large. Maximum: {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

    def _check_duplicate_filename(self, claim_id: int, filename: str) -> bool:
        """Check if filename already exists for this claim"""
        existing = self.db.query(ClaimImage).filter(
            ClaimImage.claim_id == claim_id,
            ClaimImage.image_id == filename
        ).first()
        return existing is not None

    def _get_claim_upload_dir(self, claim_id: int) -> Path:
        """
        Get upload directory for specific claim.
        Creates subdirectory structure: {IMAGES_ROOT_FOLDER}/{claim_id}/

        Args:
            claim_id: Claim ID

        Returns:
            Path object for claim's image directory
        """
        claim_dir = self.images_root / str(claim_id)
        claim_dir.mkdir(parents=True, exist_ok=True)
        return claim_dir

    def upload_image(
        self,
        claim_id: int,
        file: UploadFile,
        uploaded_by: str
    ) -> ClaimImage:
        """
        Upload image to filesystem and create database record.
        Per specification: Images can ONLY be uploaded when claim is in draft state.

        Flow:
        1. Verify claim is in draft state (ERROR if not)
        2. Store image file
        3. YOLO analyzes image
        4. Add damage report to claim
        5. Log event
        6. NO status change (remains draft)

        Args:
            claim_id: Claim ID
            file: Uploaded file
            uploaded_by: Actor identifier (e.g., "customer_100")

        Returns:
            ClaimImage instance

        Raises:
            ValidationError: If file validation fails or claim not in draft state
        """
        # Step 1: Verify claim is in 'draft' state
        claim_service = ClaimService(self.db)
        claim = claim_service.get_claim(claim_id)

        if claim.current_status != ClaimState.DRAFT.value:
            raise ValidationError(
                f"Images can only be uploaded when claim is in 'draft' state. "
                f"Current status: {claim.current_status}"
            )

        # Validate file
        self._validate_image_file(file)

        # Check for duplicate filename
        if self._check_duplicate_filename(claim_id, file.filename):
            raise ValidationError(
                f"Image '{file.filename}' already exists for this claim. "
                f"Please rename the file or delete the existing image first."
            )

        # Check max images per claim
        image_count = self.db.query(ClaimImage).filter(
            ClaimImage.claim_id == claim_id
        ).count()

        if image_count >= settings.MAX_IMAGES_PER_CLAIM:
            raise ValidationError(
                f"Maximum {settings.MAX_IMAGES_PER_CLAIM} images per claim"
            )

        # Step 2: Save file to filesystem
        claim_dir = self._get_claim_upload_dir(claim_id)
        file_path = claim_dir / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create database record
        image = ClaimImage(
            image_id=file.filename,
            claim_id=claim_id,
            uploaded_at=datetime.now(),
            uploaded_by=uploaded_by
        )

        self.db.add(image)
        self.db.flush()  # Flush to get relationships working

        # Step 3 & 4: YOLO analyzes image and create damage report
        # Get labor rate from claim
        labor_rate = float(claim.state_avg_labor_cost) if claim.state_avg_labor_cost else 140.00
        self._analyze_and_create_damage_report(
            claim_id=claim_id,
            image_id=file.filename,
            image_path=file_path,
            labor_rate=labor_rate
        )

        # Step 5: Log event
        from src.api.models.claim_event import ClaimEvent
        from datetime import date, time
        event = ClaimEvent(
            claim_id=claim_id,
            event_date=date.today(),
            event_time=datetime.now().time(),
            status=claim.current_status,
            action=ClaimAction.UPLOAD_DAMAGE_PHOTOS.value,
            action_by=ActorType.CUSTOMER.value,
            action_by_identity=uploaded_by,
            comments=f"Uploaded image: {file.filename}"
        )
        self.db.add(event)

        # Step 6: NO status change - claim remains in draft state

        self.commit()

        self.logger.info(f"Uploaded image {file.filename} for claim {claim_id}, YOLO analysis complete, damage report created")
        return image

    def _analyze_and_create_damage_report(
        self,
        claim_id: int,
        image_id: str,
        image_path: Path,
        labor_rate: float
    ) -> None:
        """
        Analyze image with YOLO and create damage reports in database.

        Args:
            claim_id: Claim ID
            image_id: Image filename
            image_path: Path to image file
            labor_rate: Labor rate in $/hour (from claim.state_avg_labor_cost)
        """
        # Get damage detector singleton
        detector = get_damage_detector()

        # Run YOLO inference
        detections = detector.detect_damages(image_path)

        if not detections:
            self.logger.warning(f"No damages detected in image {image_id} for claim {claim_id}")
            return

        # Create damage reports for each detection
        cost_service = CostService(self.db)
        estimate_id = f"{claim_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        for detection in detections:
            # Prepare damage report and assessment for cost calculation
            damage_report = {
                "part": detection.get("damage_part", "unknown"),
                "confidence": detection.get("confidence", 0.0)
            }

            assessment = {
                "severity": detection.get("severity", 0.5),
                "internal_damage_probability": detection.get("internal_damage_probability", 0.0)
            }

            # Calculate cost
            cost_breakdown = cost_service.calculate_cost(
                damage_report=damage_report,
                assessment=assessment,
                labor_rate=labor_rate
            )

            # Round labor hours to nearest 0.5 increment (industry standard)
            raw_labor_hours = float(cost_breakdown["labor_hours"])
            rounded_labor_hours = self.round_labor_hours(raw_labor_hours)
            parts_cost = float(cost_breakdown["estimated_parts_cost"])
            total_cost_rounded = (rounded_labor_hours * labor_rate) + parts_cost

            self.logger.info(
                f"Labor hours rounded: {raw_labor_hours:.2f}h → {rounded_labor_hours:.1f}h "
                f"(cost: ${total_cost_rounded:.2f})"
            )

            # Get bounding box
            bbox = detection.get("bounding_box", {})

            # Generate annotated image filename
            annotated_image_id = f"{settings.YOLO_ANNOTATED_IMAGE_PREFIX}{image_id}"

            # Create damage record with AI estimates (immutable)
            damage = Damage(
                claim_id=claim_id,
                estimate_id=estimate_id,
                image_id=image_id,
                estimate_type="ai",

                # YOLO detection data
                damage_class=detection.get("damage_class"),
                damage_confidence=detection.get("confidence"),
                damage_part=detection.get("damage_part"),
                bounding_box_x=bbox.get("x"),
                bounding_box_y=bbox.get("y"),
                bounding_box_width=bbox.get("width"),
                bounding_box_height=bbox.get("height"),

                # Assessment data (heuristic for now)
                severity=detection.get("severity"),
                internal_damage_probability=detection.get("internal_damage_probability"),
                recommended_action=detection.get("recommended_action"),
                reasoning=detection.get("reasoning"),
                car_side=detection.get("car_side"),
                assessment_confidence=detection.get("assessment_confidence"),

                # AI estimates (IMMUTABLE)
                ai_labor_hours=rounded_labor_hours,
                ai_parts_cost=parts_cost,
                ai_total_cost=total_cost_rounded,

                # Adjustor estimates (NULL initially)
                adjustor_labor_hours=None,
                adjustor_parts_cost=None,
                adjustor_total_cost=None,
                reviewed_by_adjustor=False,
                reviewed_at=None,

                avg_labor_cost=None,  # DEPRECATED: Use claim.state_avg_labor_cost

                # Annotated image reference
                annotated_image_id=annotated_image_id
            )

            self.db.add(damage)

        self.logger.info(f"Created {len(detections)} damage report(s) for claim {claim_id}, image {image_id}")

    def delete_image(
        self,
        claim_id: int,
        image_id: str,
        deleted_by: str
    ) -> None:
        """
        Delete image from filesystem and database.
        Cascade deletes associated damages (ON DELETE CASCADE).

        Args:
            claim_id: Claim ID
            image_id: Image filename
            deleted_by: Actor identifier

        Raises:
            ResourceNotFoundError: If image doesn't exist
        """
        # Get image record
        image = self.db.query(ClaimImage).filter(
            ClaimImage.claim_id == claim_id,
            ClaimImage.image_id == image_id
        ).first()

        if not image:
            raise ResourceNotFoundError("Image", image_id)

        # Delete from filesystem
        claim_dir = self._get_claim_upload_dir(claim_id)
        file_path = claim_dir / image_id

        if file_path.exists():
            file_path.unlink()

        # Get claim for event logging
        from src.api.services.claim_service import ClaimService
        claim_service = ClaimService(self.db)
        claim = claim_service.get_claim(claim_id)

        # Delete from database (cascade deletes damages)
        self.db.delete(image)

        # Log event
        from src.api.models.claim_event import ClaimEvent
        from datetime import date
        event = ClaimEvent(
            claim_id=claim_id,
            event_date=date.today(),
            event_time=datetime.now().time(),
            status=claim.current_status,
            action=ClaimAction.IMAGE_DELETED.value,
            action_by=ActorType.CUSTOMER.value,
            action_by_identity=deleted_by,
            comments=f"Deleted image: {image_id}"
        )
        self.db.add(event)

        self.commit()

        self.logger.info(f"Deleted image {image_id} from claim {claim_id}")

    def get_image_path(self, claim_id: int, image_id: str) -> Path:
        """Get full path to image file"""
        return self._get_claim_upload_dir(claim_id) / image_id
