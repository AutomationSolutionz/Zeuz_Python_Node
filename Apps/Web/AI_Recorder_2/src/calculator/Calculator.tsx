import { calculatorKeys } from './calculatorData'
import { CalculatorDisplay } from './CalculatorDisplay'
import { CalculatorKeypad } from './CalculatorKeypad'
import { useCalculator } from './useCalculator'

export function Calculator() {
  const calculator = useCalculator()

  return (
    <article className="calculator-card" aria-label="Modern calculator">
      <header className="calculator-card__header">
        <div>
          <span className="calculator-card__eyebrow">REQ-120</span>
          <h2>Calculator</h2>
        </div>
        <span className="calculator-card__badge">Live</span>
      </header>
      <CalculatorDisplay
        displayValue={calculator.displayValue}
        errorMessage={calculator.errorMessage}
        expression={calculator.expression}
        statusText={calculator.statusText}
      />
      <CalculatorKeypad
        activeOperator={calculator.pendingOperator}
        keys={calculatorKeys}
        onKeyPress={calculator.pressKey}
      />
    </article>
  )
}
