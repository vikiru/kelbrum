import type { ComponentProps } from 'react';

import { Field as FieldPrimitive } from '@base-ui/react/field';

import { cn } from '@/shared/lib/utils';

function Field({ className, ...props }: ComponentProps<typeof FieldPrimitive.Root>) {
  return <FieldPrimitive.Root data-slot="field" className={cn('flex flex-col gap-2', className)} {...props} />;
}

function FieldLabel({ className, ...props }: ComponentProps<typeof FieldPrimitive.Label>) {
  return (
    <FieldPrimitive.Label
      data-slot="field-label"
      className={cn('font-heading text-sm font-medium', className)}
      {...props}
    />
  );
}

function FieldDescription({ className, ...props }: ComponentProps<typeof FieldPrimitive.Description>) {
  return (
    <FieldPrimitive.Description
      data-slot="field-description"
      className={cn('text-sm leading-relaxed text-muted-foreground', className)}
      {...props}
    />
  );
}

function FieldError({ className, ...props }: ComponentProps<typeof FieldPrimitive.Error>) {
  return (
    <FieldPrimitive.Error
      data-slot="field-error"
      className={cn('text-sm leading-relaxed text-destructive', className)}
      {...props}
    />
  );
}

export { Field, FieldDescription, FieldError, FieldLabel };
