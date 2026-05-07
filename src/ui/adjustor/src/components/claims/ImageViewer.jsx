/**
 * ImageViewer component with zoom/pan and bounding box overlay
 */
import { useState } from 'react';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';
import { ZoomIn, ZoomOut, Maximize2, ChevronLeft, ChevronRight, Eye, EyeOff } from 'lucide-react';

const ImageViewer = ({ images, damages = [] }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showBoundingBoxes, setShowBoundingBoxes] = useState(true);

  if (!images || images.length === 0) {
    return (
      <div className="bg-gray-100 rounded-lg p-8 text-center">
        <p className="text-gray-500">No images available</p>
      </div>
    );
  }

  const currentImage = images[currentIndex];

  // Filter damages for current image
  const currentImageDamages = damages.filter(
    (d) => d.image_id === currentImage.image_id
  );

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : images.length - 1));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev < images.length - 1 ? prev + 1 : 0));
  };

  return (
    <div className="bg-gray-50 rounded-lg border border-gray-200 overflow-hidden">
      {/* Controls */}
      <div className="bg-white border-b border-gray-200 p-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">
            Image {currentIndex + 1} of {images.length}
          </span>
          {currentImageDamages.length > 0 && (
            <span className="text-xs text-gray-500">
              ({currentImageDamages.length} damage{currentImageDamages.length > 1 ? 's' : ''})
            </span>
          )}
        </div>

        <button
          onClick={() => setShowBoundingBoxes(!showBoundingBoxes)}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            showBoundingBoxes
              ? 'bg-primary-100 text-primary-700'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          {showBoundingBoxes ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
          Bounding Boxes
        </button>
      </div>

      {/* Image Viewer */}
      <div className="relative bg-gray-900" style={{ height: '500px' }}>
        <TransformWrapper
          initialScale={1}
          minScale={0.5}
          maxScale={4}
          centerOnInit={true}
        >
          {({ zoomIn, zoomOut, resetTransform }) => (
            <>
              {/* Zoom Controls */}
              <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
                <button
                  onClick={() => zoomIn()}
                  className="bg-white/90 hover:bg-white p-2 rounded-lg shadow-lg transition-colors"
                  aria-label="Zoom in"
                >
                  <ZoomIn className="h-5 w-5 text-gray-700" />
                </button>
                <button
                  onClick={() => zoomOut()}
                  className="bg-white/90 hover:bg-white p-2 rounded-lg shadow-lg transition-colors"
                  aria-label="Zoom out"
                >
                  <ZoomOut className="h-5 w-5 text-gray-700" />
                </button>
                <button
                  onClick={() => resetTransform()}
                  className="bg-white/90 hover:bg-white p-2 rounded-lg shadow-lg transition-colors"
                  aria-label="Reset zoom"
                >
                  <Maximize2 className="h-5 w-5 text-gray-700" />
                </button>
              </div>

              {/* Navigation Arrows */}
              {images.length > 1 && (
                <>
                  <button
                    onClick={handlePrevious}
                    className="absolute left-4 top-1/2 -translate-y-1/2 z-10 bg-white/90 hover:bg-white p-3 rounded-full shadow-lg transition-colors"
                    aria-label="Previous image"
                  >
                    <ChevronLeft className="h-6 w-6 text-gray-700" />
                  </button>
                  <button
                    onClick={handleNext}
                    className="absolute right-4 top-1/2 -translate-y-1/2 z-10 bg-white/90 hover:bg-white p-3 rounded-full shadow-lg transition-colors"
                    aria-label="Next image"
                  >
                    <ChevronRight className="h-6 w-6 text-gray-700" />
                  </button>
                </>
              )}

              {/* Transformable Image */}
              <TransformComponent
                wrapperStyle={{ width: '100%', height: '100%' }}
                contentStyle={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
              >
                <div className="relative">
                  {/* Display annotated image when bounding boxes are ON, otherwise original */}
                  <img
                    src={showBoundingBoxes && currentImage.annotated_url ? currentImage.annotated_url : currentImage.image_url}
                    alt={`Damage ${currentIndex + 1}`}
                    className="max-w-full max-h-[500px] object-contain"
                  />

                  {/* Show message if bounding boxes are ON but annotated image is not available */}
                  {showBoundingBoxes && !currentImage.annotated_url && currentImageDamages.length > 0 && (
                    <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-yellow-100 border border-yellow-300 text-yellow-800 px-4 py-2 rounded-lg text-sm shadow-lg">
                      Annotated image with bounding boxes not available
                    </div>
                  )}
                </div>
              </TransformComponent>
            </>
          )}
        </TransformWrapper>
      </div>

      {/* Image Info */}
      <div className="bg-white border-t border-gray-200 p-3">
        <p className="text-sm text-gray-600">
          {currentImage.view_angle && (
            <span className="font-medium">{currentImage.view_angle}</span>
          )}
          {currentImage.uploaded_at && (
            <span className="ml-2 text-gray-500">
              · Uploaded {new Date(currentImage.uploaded_at).toLocaleDateString()}
            </span>
          )}
        </p>
      </div>
    </div>
  );
};

export default ImageViewer;
