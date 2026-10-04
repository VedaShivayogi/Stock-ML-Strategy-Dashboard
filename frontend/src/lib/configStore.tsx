import { createContext, useContext, useState, ReactNode } from 'react';

interface Config {
  ticker1: string;
  ticker2: string;
  beginnerMode: boolean;
  compareMode: boolean;
  model: string;
  years: number;
  trainRatio: number;
  startMoney: number;
}

interface ConfigContextType {
  config: Config;
  setConfig: (updates: Partial<Config>) => void;
}

const defaultConfig: Config = {
  ticker1: 'SPY',
  ticker2: 'AAPL',
  beginnerMode: false,
  compareMode: false,
  model: 'random_forest',
  years: 10,
  trainRatio: 0.8,
  startMoney: 100,
};

const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

export function ConfigProvider({ children }: { children: ReactNode }) {
  const [config, setConfigState] = useState<Config>(defaultConfig);

  const setConfig = (updates: Partial<Config>) => {
    setConfigState(prev => ({ ...prev, ...updates }));
  };

  return (
    <ConfigContext.Provider value={{ config, setConfig }}>
      {children}
    </ConfigContext.Provider>
  );
}

export function useConfig() {
  const context = useContext(ConfigContext);
  if (!context) throw new Error('useConfig must be used within a ConfigProvider');
  return context;
}
