import type { PropsWithChildren } from 'react';

export interface PageContainerProps {
  className?: string;
}

export function PageContainer({ children, className = '' }: PropsWithChildren<PageContainerProps>) {
  return (
    <div
      className={`mx-auto w-[calc(100%-2rem)] max-w-[1600px] lg:w-[calc(100%-4rem)] 2xl:w-[calc(100%-6rem)] ${className}`}
    >
      {children}
    </div>
  );
}
