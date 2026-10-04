import { useQuery } from '@tanstack/react-query';
import { useConfig } from '../lib/configStore';
import Card from '../components/Card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';

export default function Explain() {
  const { config } = useConfig();
  
  const fetchShap = async (ticker: string) => {
    const res = await fetch(`http://localhost:8000/api/shap/importance?ticker=${ticker}&years=${config.years}&train_ratio=${config.trainRatio}&model=${config.model}&start_money=${config.startMoney}`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Network error');
    }
    return res.json();
  };

  const { data, isLoading, error } = useQuery({
    queryKey: ['shap', config.ticker1, config.years, config.trainRatio, config.model, config.startMoney],
    queryFn: () => fetchShap(config.ticker1),
    staleTime: Infinity,
    retry: false,
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-2xl font-bold mb-1">Explainability (SHAP)</h1>
        <p className="text-secondaryText text-sm">Understanding model feature importance for {config.ticker1}.</p>
      </div>

      {config.beginnerMode && (
        <div className="bg-primaryBlue/10 border-l-4 border-primaryBlue rounded-r-md p-4 mb-4 text-sm text-primaryBlue">
          <strong>💡 Beginner Mode:</strong> The model looks at 19 different signals before making each prediction.
          SHAP measures how much each signal *actually influenced* the model's decision. Longer bar = bigger influence.
        </div>
      )}

      {config.model === 'ensemble' ? (
        <div className="p-8 text-center text-secondaryText">Switch to a single model (not ensemble) to see SHAP values.</div>
      ) : isLoading ? (
        <div className="p-8 text-center text-secondaryText">Computing SHAP values...</div>
      ) : error ? (
        <div className="p-8 text-center text-negativeRed">{(error as Error).message}</div>
      ) : data ? (
        <Card className="h-[600px]">
          <h3 className="font-semibold mb-4">Feature Importance — {config.ticker1}</h3>
          <div className="h-[500px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={data} margin={{ top: 5, right: 30, left: 100, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="var(--color-cardBorder)" />
                <XAxis type="number" tick={{fontSize: 12, fill: 'var(--color-secondaryText)'}} axisLine={false} tickLine={false} />
                <YAxis dataKey="feature" type="category" tick={{fontSize: 12, fill: 'var(--color-primaryText)'}} axisLine={false} tickLine={false} width={150} />
                <RechartsTooltip 
                  cursor={{fill: 'var(--color-cardBorder)', opacity: 0.4}}
                  contentStyle={{ backgroundColor: 'var(--color-cardBg)', borderColor: 'var(--color-cardBorder)', borderRadius: '8px' }}
                />
                <Bar dataKey="mean_abs_shap" fill="#0B5FFF" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      ) : null}
    </div>
  );
}
