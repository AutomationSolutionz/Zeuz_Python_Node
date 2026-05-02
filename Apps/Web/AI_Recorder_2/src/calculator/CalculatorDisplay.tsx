type CalculatorDisplayProps = {
  expression: string
  displayValue: string
  statusText: string
  errorMessage: string | null
}

export function CalculatorDisplay({ expression, displayValue, statusText, errorMessage }: CalculatorDisplayProps) {
  const hasLongValue = displayValue.length > 12

  return (
    <section className="calculator-display" aria-label="Calculator display">
      <div className="calculator-display__topline">
        <span>{expression || 'Enter an expression'}</span>
        <span>{statusText}</span>
      </div>
      <output
        className={`calculator-display__value${hasLongValue ? ' calculator-display__value--compact' : ''}`}
        aria-live="polite"
      >
        {displayValue}
      </output>
      <p className="calculator-display__message" role={errorMessage ? 'alert' : 'status'}>
        {errorMessage || 'Basic arithmetic with clear, delete, percent, and repeated equals support.'}
      </p>
    </section>
  )
}
