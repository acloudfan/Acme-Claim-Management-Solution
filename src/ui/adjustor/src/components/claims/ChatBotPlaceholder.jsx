/**
 * ChatBotPlaceholder - Placeholder for future AI Research Assistant
 */
import { Bot, Sparkles } from 'lucide-react';
import Card from '../common/Card';

const ChatBotPlaceholder = () => {
  return (
    <div className="h-full flex flex-col">
      <Card className="flex-1 flex flex-col">
        <div className="text-center py-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
            <Bot className="h-8 w-8 text-primary-600" />
          </div>

          <h3 className="text-xl font-semibold text-gray-900 mb-2 flex items-center justify-center gap-2">
            <Sparkles className="h-5 w-5 text-amber-500" />
            AI Research Assistant
          </h3>

          <p className="text-sm font-medium text-amber-600 mb-4">Coming Soon</p>

          <div className="text-left max-w-sm mx-auto space-y-4">
            <p className="text-sm text-gray-600">
              A natural language assistant to help you research and validate claim details.
            </p>

            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-xs font-semibold text-gray-700 mb-2">Planned Features:</p>
              <ul className="text-xs text-gray-600 space-y-1.5">
                <li className="flex items-start">
                  <span className="text-primary-600 mr-2">•</span>
                  <span>Repair procedure lookup and guidance</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-600 mr-2">•</span>
                  <span>Parts pricing and availability checks</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-600 mr-2">•</span>
                  <span>Labor time standards (Mitchell, AllData)</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-600 mr-2">•</span>
                  <span>Policy coverage interpretation</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-600 mr-2">•</span>
                  <span>Damage assessment best practices</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-600 mr-2">•</span>
                  <span>Regulatory compliance guidance</span>
                </li>
              </ul>
            </div>

            <div className="text-xs text-gray-500 italic">
              This feature will be available in a future release.
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ChatBotPlaceholder;
