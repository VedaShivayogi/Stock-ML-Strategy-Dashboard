import { useQuery } from '@tanstack/react-query';
import { useConfig } from '../lib/configStore';
import Card from '../components/Card';
import { formatMoney, formatPercent, formatNumber, cn } from '../lib/utils';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function Dashboard() {
  const { config } = useConfig();
  
  const fetchRunData = async (ticker: string) => {
    const res = await fetch(`http://localhost:8000/api/run?ticker=${ticker}&years=${config.years}&train_ratio=${config.trainRatio}&model=${config.model}&start_money=${config.startMoney}`);
    if (!res.ok) throw new Error('Network response was not ok');
    return res.json();
  };

  const { data: data1, isLoading: isLoading1, error: error1 } = useQuery({
    queryKey: ['runData', config.ticker1, config.years, config.trainRatio, config.model, config.startMoney],
    queryFn: () => fetchRunData(config.ticker1),
    staleTime: Infinity,
  });

  const { data: data2 } = useQuery({
    queryKey: ['runData', config.ticker2, config.years, config.trainRatio, config.model, config.startMoney],
    queryFn: () => fetchRunData(config.ticker2),
    enabled: config.compareMode && !!config.ticker2,
    staleTime: Infinity,
  });

  if (isLoading1) return <div className="p-8 text-center text-secondaryText">Loading {config.ticker1} data...</div>;
  if (error1) return <div className="p-8 text-center text-negativeRed">Error loading data. Check ticker and try again.</div>;
  if (!data1) return null;

  const chartData = data1.dates.map((date: string, i: number) => {
    const point: any = { date };
    point[`${config.ticker1} ML`] = data1.ml_wealth[i];
    point[`${config.ticker1} B&H`] = data1.buy_hold[i];
    
    if (config.compareMode && data2) {
      point[`${config.ticker2} ML`] = data2.ml_wealth[i];
      point[`${config.ticker2} B&H`] = data2.buy_hold[i];
    }
    return point;
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-2xl font-bold mb-1">Dashboard</h1>
        <p className="text-secondaryText text-sm">Overview of ML strategy performance vs Buy & Hold.</p>
      </div>

      {config.beginnerMode && (
        <div className="bg-primaryBlue/10 border-l-4 border-primaryBlue rounded-r-md p-4 mb-4 text-sm text-primaryBlue">
          <strong>💡 Beginner Mode:</strong> These numbers summarize how well each strategy performed. 
          Sharpe ratio measures return per unit of risk. Max Drawdown is the worst loss from a peak. 
          Hit Rate is the % of days the model predicted the right direction.
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricCard title={`Sharpe (B&H)`} value={data1.metrics.sharpe_bh} formatter={formatNumber} />
        <MetricCard title={`Sharpe (ML)`} value={data1.metrics.sharpe_ml} formatter={formatNumber} highlight />
        <MetricCard title={`MaxDD (B&H)`} value={data1.metrics.maxdd_bh} formatter={formatPercent} />
        <MetricCard title={`MaxDD (ML)`} value={data1.metrics.maxdd_ml} formatter={formatPercent} highlight />
        <MetricCard title={`Hit Rate`} value={data1.metrics.hit_rate} formatter={formatPercent} />
        <MetricCard title={`Sortino (ML)`} value={data1.metrics.sortino_ml} formatter={formatNumber} />
      </div>

      <Card className="h-[450px]">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">Wealth Curves</h3>
        </div>
        <div className="h-[350px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-cardBorder)" />
              <XAxis dataKey="date" tick={{fontSize: 12, fill: 'var(--color-secondaryText)'}} axisLine={false} tickLine={false} minTickGap={30} />
              <YAxis tickFormatter={(v) => `$${v}`} tick={{fontSize: 12, fill: 'var(--color-secondaryText)'}} axisLine={false} tickLine={false} width={60} />
              <Tooltip 
                contentStyle={{ backgroundColor: 'var(--color-cardBg)', borderColor: 'var(--color-cardBorder)', borderRadius: '8px' }}
                itemStyle={{ fontSize: '14px', fontWeight: 500 }}
                labelStyle={{ color: 'var(--color-secondaryText)', marginBottom: '8px' }}
                formatter={(value: number) => formatMoney(value)}
              />
              <Legend wrapperStyle={{ fontSize: '13px' }} />
              
              <Line type="monotone" dataKey={`${config.ticker1} B&H`} stroke="#16A34A" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey={`${config.ticker1} ML`} stroke="#7C3AED" strokeWidth={2} dot={false} strokeDasharray="5 5" />
              
              {config.compareMode && data2 && (
                <>
                  <Line type="monotone" dataKey={`${config.ticker2} B&H`} stroke="#0B5FFF" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey={`${config.ticker2} ML`} stroke="#F59E0B" strokeWidth={2} dot={false} strokeDasharray="5 5" />
                </>
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>
      
      <Card>
        <h3 className="font-semibold mb-4">Recent Daily Positions ({config.ticker1})</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-secondaryText uppercase bg-appBg/50 border-y border-cardBorder">
              <tr>
                <th className="px-4 py-3 font-medium">Date</th>
                <th className="px-4 py-3 font-medium">Close ($)</th>
                <th className="px-4 py-3 font-medium">Predicted Return</th>
                <th className="px-4 py-3 font-medium">Position</th>
                <th className="px-4 py-3 font-medium">Actual Return</th>
                <th className="px-4 py-3 font-medium text-center">Correct?</th>
              </tr>
            </thead>
            <tbody>
              {data1.dates.slice(-30).map((date: string, i: number) => {
                const originalIndex = data1.dates.length - 30 + i;
                if (originalIndex < 0) return null; 
                
                const pos = data1.positions[originalIndex];
                const pred = data1.preds[originalIndex];
                const actual = data1.actual_returns[originalIndex];
                const isCorrect = Math.sign(pred) === Math.sign(actual) || (pred === 0 && actual === 0);
                
                return (
                  <tr key={date} className="border-b border-cardBorder hover:bg-appBg/50 transition-colors">
                    <td className="px-4 py-3 font-medium">{date}</td>
                    <td className="px-4 py-3 tabular-nums">{formatMoney(data1.close[originalIndex])}</td>
                    <td className="px-4 py-3 tabular-nums">{pred.toFixed(4)}</td>
                    <td className="px-4 py-3">
                      <span className={cn(
                        "px-2.5 py-1 rounded-full text-xs font-semibold",
                        pos > 0 ? "bg-positiveGreen/10 text-positiveGreen" : "bg-negativeRed/10 text-negativeRed"
                      )}>
                        {pos > 0 ? "LONG" : "SHORT"}
                      </span>
                    </td>
                    <td className={cn("px-4 py-3 tabular-nums font-medium", actual > 0 ? "text-positiveGreen" : actual < 0 ? "text-negativeRed" : "")}>
                      {actual.toFixed(4)}
                    </td>
                    <td className="px-4 py-3 text-center text-lg">{isCorrect ? '✅' : '❌'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

function MetricCard({ title, value, formatter, highlight = false }: { title: string, value: number, formatter: (v: number) => string, highlight?: boolean }) {
  return (
    <Card className={cn("flex flex-col gap-1 p-4", highlight && "border-primaryBlue/30 bg-primaryBlue/5")}>
      <span className="text-xs text-secondaryText font-medium uppercase tracking-wider">{title}</span>
      <span className="text-xl font-bold font-inter tracking-tight tabular-nums">{formatter(value)}</span>
    </Card>
  );
}
