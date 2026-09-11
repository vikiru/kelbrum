import type { ComponentProps } from 'react';

import { Field as FieldPrimitive } from '@base-ui/react/field';

import { cn } from '@/shared/lib/utils';

function Label({ className, ...props }: ComponentProps<'label'>) {
  return (
    <FieldPrimitive.Label
      data-slot="label"
      className={cn(
        'text-sm leading-none font-medium select-none group-data-[disabled=true]/field:pointer-events-none group-data-[disabled=true]/field:opacity-50 peer-disabled:cursor-not-allowed peer-disabled:opacity-50',
        className,
      )}
      {...props}
    />
  );
}

export { Label };
