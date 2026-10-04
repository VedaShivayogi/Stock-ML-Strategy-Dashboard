import Card from '../components/Card';
import { PlayCircle, BookOpen, TrendingUp } from 'lucide-react';

export default function Community() {
  const articles = [
    { title: "Understanding Sharpe Ratio", category: "Learn", icon: TrendingUp, desc: "A deep dive into measuring risk-adjusted returns and why it matters." },
    { title: "What is Max Drawdown?", category: "Learn", icon: TrendingUp, desc: "How to interpret the worst possible loss from a peak." },
    { title: "Intro to SHAP Values", category: "Explainability", icon: BookOpen, desc: "Open the black box of machine learning models with game theory." },
    { title: "Monte Carlo Simulations", category: "Risk", icon: PlayCircle, desc: "Why we use randomness to predict the future." },
  ];

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between border-b border-cardBorder pb-4">
        <div>
          <h1 className="text-2xl font-bold mb-1">Community & Learn</h1>
          <p className="text-secondaryText text-sm">Educational resources to understand your ML dashboard.</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-primaryBlue text-white rounded-btn text-sm font-medium">Latest</button>
          <button className="px-4 py-2 text-secondaryText hover:bg-cardBorder/50 rounded-btn text-sm font-medium transition-colors">Popular</button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {articles.map((article, i) => (
          <Card key={i} className="hover:shadow-soft-dark transition-shadow cursor-pointer group flex flex-col h-full">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-primaryBlue/10 flex items-center justify-center text-primaryBlue group-hover:scale-110 transition-transform">
                <article.icon size={20} />
              </div>
              <span className="text-xs font-semibold text-primaryBlue uppercase tracking-wider">{article.category}</span>
            </div>
            <h3 className="text-lg font-bold mb-2 group-hover:text-primaryBlue transition-colors">{article.title}</h3>
            <p className="text-secondaryText text-sm flex-1">{article.desc}</p>
            <div className="mt-6 pt-4 border-t border-cardBorder flex justify-between items-center text-xs text-secondaryText">
              <span>Read article</span>
              <span>→</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
