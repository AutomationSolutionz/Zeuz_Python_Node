import { CalculatorKey, CalculatorKeyValue, Operator } from './calculatorData'

type CalculatorKeypadProps = {
  keys: CalculatorKey[]
  activeOperator: Operator | null
  onKeyPress: (value: CalculatorKeyValue) => void
}

export function CalculatorKeypad({ keys, activeOperator, onKeyPress }: CalculatorKeypadProps) {
  return (
    <div className="calculator-keypad" role="group" aria-label="Calculator keypad">
      {keys.map((key) => {
        const isActiveOperator = key.type === 'operator' && key.value === activeOperator
        const className = [
          'calculator-key',
          `calculator-key--${key.type}`,
          key.span === 'double' ? 'calculator-key--double' : '',
          isActiveOperator ? 'calculator-key--active' : '',
        ].filter(Boolean).join(' ')

        return (
          <button
            aria-label={key.ariaLabel}
            className={className}
            key={key.value}
            onClick={() => onKeyPress(key.value)}
            type="button"
          >
            {key.label}
          </button>
        )
      })}
    </div>
  )
}
