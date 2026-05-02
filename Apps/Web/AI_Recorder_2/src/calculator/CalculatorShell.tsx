import { Calculator } from './Calculator'
import './calculator.css'

export function CalculatorShell() {
  return (
    <main className="calculator-page">
      <section className="calculator-hero" aria-labelledby="calculator-title">
        <div className="calculator-hero__content">
          <span className="calculator-hero__label">Modern web calculator</span>
          <h1 id="calculator-title">Black surface. White digits. Production-ready interactions.</h1>
          <p>
            A responsive calculator component built with Space Grotesk, strong contrast, and graceful handling for long expressions, invalid input, and repeated operations.
          </p>
          <div className="calculator-hero__details" aria-label="Calculator capabilities">
            <span>Sequential arithmetic</span>
            <span>Overflow-safe display</span>
            <span>Keyboard ready</span>
          </div>
        </div>
        <Calculator />
      </section>
    </main>
  )
}
