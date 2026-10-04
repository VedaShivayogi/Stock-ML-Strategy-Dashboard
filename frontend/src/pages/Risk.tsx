import { useQuery } from '@tanstack/react-query';
import { useConfig } from '../lib/configStore';
import Card from '../components/Card';
import { formatMoney } from '../lib/utils';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, ErrorBar, Cell } from 'recharts';

export default function Risk() {
  const { config } = useConfig();
  
  const fetchMonteCarlo = async (ticker: string) => {
    const res = await fetch(`http://localhost:8000/api/montecarlo?ticker=${ticker}&years=${config.years}&train_ratio=${config.trainRatio}&model=${config.model}&start_money=${config.startMoney}`);
    if (!res.ok) throw new Error('Network response was not ok');
    return res.json();
  };

  const { data, isLoading, error } = useQuery({
    queryKey: ['montecarlo', config.ticker1, config.years, config.trainRatio, config.model, config.startMoney],
    queryFn: () => fetchMonteCarlo(config.ticker1),
    staleTime: Infinity,
  });

  if (isLoading) return <div className="p-8 text-center text-secondaryText">Loading Monte Carlo simulations...</div>;
  if (error) return <div className="p-8 text-center text-negativeRed">Error loading data.</div>;
  if (!data) return null;

  const barData = [
    {
      name: 'Buy & Hold',
      median: data.bh_p50,
      p5: data.bh_p5,
      p95: data.bh_p95,
      errorY: [data.bh_p50 - data.bh_p5, data.bh_p95 - data.bh_p50],
      fill: '#16A34A',
    },
    {
      name: 'ML Strategy',
      median: data.ml_p50,
      p5: data.ml_p5,
      p95: data.ml_p95,
      errorY: [data.ml_p50 - data.ml_p5, data.ml_p95 - data.ml_p50],
      fill: '#7C3AED',
    }
  ];

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-2xl font-bold mb-1">Risk Analysis (Monte Carlo)</h1>
        <p className="text-secondaryText text-sm">Simulating 500 possible market paths for {config.ticker1}.</p>
      </div>

      {config.beginnerMode && (
        <div className="bg-primaryBlue/10 border-l-4 border-primaryBlue rounded-r-md p-4 mb-4 text-sm text-primaryBlue">
          <strong>💡 Beginner Mode:</strong> Monte Carlo simulation shuffles historical returns to create 500 alternative reality paths. 
          The chart below shows the median outcome (the bar) and the 5th-95th percentile range (the line). A tighter range means more predictable outcomes.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4 flex flex-col gap-1">
          <span className="text-xs text-secondaryText font-medium uppercase tracking-wider">ML Median</span>
          <span className="text-xl font-bold font-inter tracking-tight tabular-nums">{formatMoney(data.ml_p50)}</span>
        </Card>
        <Card className="p-4 flex flex-col gap-1">
          <span className="text-xs text-secondaryText font-medium uppercase tracking-wider">ML 5th–95th</span>
          <span className="text-lg font-bold font-inter tracking-tight tabular-nums">{formatMoney(data.ml_p5)} - {formatMoney(data.ml_p95)}</span>
        </Card>
        <Card className="p-4 flex flex-col gap-1">
          <span className="text-xs text-secondaryText font-medium uppercase tracking-wider">B&H Median</span>
          <span className="text-xl font-bold font-inter tracking-tight tabular-nums">{formatMoney(data.bh_p50)}</span>
        </Card>
        <Card className="p-4 flex flex-col gap-1">
          <span className="text-xs text-secondaryText font-medium uppercase tracking-wider">B&H 5th–95th</span>
          <span className="text-lg font-bold font-inter tracking-tight tabular-nums">{formatMoney(data.bh_p5)} - {formatMoney(data.bh_p95)}</span>
        </Card>
      </div>

      <Card className="h-[400px]">
        <h3 className="font-semibold mb-4">Median and 5th–95th percentile</h3>
        <div className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }} barSize={60}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-cardBorder)" />
              <XAxis dataKey="name" tick={{fontSize: 14, fill: 'var(--color-secondaryText)'}} axisLine={false} tickLine={false} />
              <YAxis tickFormatter={(v) => `$${v}`} tick={{fontSize: 12, fill: 'var(--color-secondaryText)'}} axisLine={false} tickLine={false} />
              <RechartsTooltip 
                cursor={{fill: 'transparent'}}
                contentStyle={{ backgroundColor: 'var(--color-cardBg)', borderColor: 'var(--color-cardBorder)', borderRadius: '8px' }}
                formatter={(val: number) => formatMoney(val)}
              />
              <Bar dataKey="median" radius={[4, 4, 0, 0]}>
                {barData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} fillOpacity={0.7} />
                ))}
                <ErrorBar dataKey="errorY" width={10} strokeWidth={2} stroke="var(--color-primaryText)" />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}
