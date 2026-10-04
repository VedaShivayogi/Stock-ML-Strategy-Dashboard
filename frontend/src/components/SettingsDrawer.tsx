import { X } from 'lucide-react';
import { useConfig } from '../lib/configStore';
import { useQueryClient } from '@tanstack/react-query';

export default function SettingsDrawer({ onClose }: { onClose: () => void }) {
  const { config, setConfig } = useConfig();
  const queryClient = useQueryClient();

  const handleRun = () => {
    queryClient.invalidateQueries({ queryKey: ['runData'] });
    onClose();
  };

  return (
    <div className="flex flex-col h-full bg-cardBg text-primaryText">
      <div className="flex items-center justify-between p-4 border-b border-cardBorder">
        <h2 className="font-semibold text-lg">Settings</h2>
        <button onClick={onClose} className="p-1 rounded-md hover:bg-cardBorder/50 text-secondaryText">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        <div>
          <label className="flex items-center justify-between cursor-pointer">
            <span className="font-medium text-sm">Beginner Mode</span>
            <input 
              type="checkbox" 
              checked={config.beginnerMode}
              onChange={(e) => setConfig({ beginnerMode: e.target.checked })}
              className="sr-only peer"
            />
            <div className="relative w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primaryBlue"></div>
          </label>
          <p className="text-xs text-secondaryText mt-1">Shows friendly explanations above each chart.</p>
        </div>

        <div>
          <label className="flex items-center justify-between cursor-pointer">
            <span className="font-medium text-sm">Compare Mode</span>
            <input 
              type="checkbox" 
              checked={config.compareMode}
              onChange={(e) => setConfig({ compareMode: e.target.checked })}
              className="sr-only peer"
            />
            <div className="relative w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primaryBlue"></div>
          </label>
        </div>
        
        <div className="space-y-3">
          <h3 className="font-medium text-sm border-b border-cardBorder pb-2">Tickers</h3>
          <div>
            <label className="block text-xs text-secondaryText mb-1">Primary Ticker</label>
            <input 
              type="text"
              value={config.ticker1}
              onChange={(e) => setConfig({ ticker1: e.target.value.toUpperCase() })}
              className="w-full bg-appBg border border-cardBorder rounded-btn px-3 py-2 text-sm focus:outline-none focus:border-primaryBlue"
            />
          </div>
          {config.compareMode && (
            <div>
              <label className="block text-xs text-secondaryText mb-1">Secondary Ticker</label>
              <input 
                type="text"
                value={config.ticker2}
                onChange={(e) => setConfig({ ticker2: e.target.value.toUpperCase() })}
                className="w-full bg-appBg border border-cardBorder rounded-btn px-3 py-2 text-sm focus:outline-none focus:border-primaryBlue"
              />
            </div>
          )}
        </div>

        <div className="space-y-3">
          <h3 className="font-medium text-sm border-b border-cardBorder pb-2">Model Configuration</h3>
          
          <div>
            <label className="block text-xs text-secondaryText mb-1">Model</label>
            <select 
              value={config.model}
              onChange={(e) => setConfig({ model: e.target.value })}
              className="w-full bg-appBg border border-cardBorder rounded-btn px-3 py-2 text-sm focus:outline-none focus:border-primaryBlue"
            >
              <option value="random_forest">Random Forest</option>
              <option value="xgboost">XGBoost</option>
              <option value="lightgbm">LightGBM</option>
              <option value="ensemble">Ensemble</option>
            </select>
          </div>

          <div>
            <label className="block text-xs text-secondaryText mb-1">Years of data ({config.years})</label>
            <input 
              type="range" min="2" max="15" 
              value={config.years}
              onChange={(e) => setConfig({ years: parseInt(e.target.value) })}
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-xs text-secondaryText mb-1">Train Ratio ({config.trainRatio})</label>
            <input 
              type="range" min="0.6" max="0.9" step="0.05"
              value={config.trainRatio}
              onChange={(e) => setConfig({ trainRatio: parseFloat(e.target.value) })}
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-xs text-secondaryText mb-1">Starting money ($)</label>
            <input 
              type="number"
              value={config.startMoney}
              onChange={(e) => setConfig({ startMoney: parseFloat(e.target.value) })}
              className="w-full bg-appBg border border-cardBorder rounded-btn px-3 py-2 text-sm focus:outline-none focus:border-primaryBlue"
            />
          </div>
        </div>
      </div>

      <div className="p-4 border-t border-cardBorder">
        <button 
          onClick={handleRun}
          className="w-full bg-primaryBlue text-white py-2 rounded-btn font-medium hover:bg-primaryBlue/90 transition-colors"
        >
          Run Pipeline
        </button>
      </div>
    </div>
  );
}
