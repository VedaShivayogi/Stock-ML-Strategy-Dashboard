import { ReactNode } from 'react';
import { cn } from '../lib/utils';

interface CardProps {
  children: ReactNode;
  className?: string;
}

export default function Card({ children, className }: CardProps) {
  return (
    <div className={cn("bg-cardBg border border-cardBorder rounded-card shadow-soft dark:shadow-soft-dark p-5", className)}>
      {children}
    </div>
  );
}
