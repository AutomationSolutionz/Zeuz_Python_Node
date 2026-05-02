export type Operator = 'add' | 'subtract' | 'multiply' | 'divide'

export type CalculatorKeyType = 'digit' | 'operator' | 'utility' | 'equals' | 'decimal'

export type CalculatorKeyValue =
  | '0'
  | '1'
  | '2'
  | '3'
  | '4'
  | '5'
  | '6'
  | '7'
  | '8'
  | '9'
  | '.'
  | 'clear'
  | 'backspace'
  | 'percent'
  | 'equals'
  | Operator

export interface CalculatorKey {
  label: string
  value: CalculatorKeyValue
  type: CalculatorKeyType
  ariaLabel: string
  span?: 'double'
}

export const operatorSymbols: Record<Operator, string> = {
  add: '+',
  subtract: '−',
  multiply: '×',
  divide: '÷',
}

export const calculatorKeys: CalculatorKey[] = [
  { label: 'AC', value: 'clear', type: 'utility', ariaLabel: 'Clear calculator' },
  { label: 'DEL', value: 'backspace', type: 'utility', ariaLabel: 'Delete last digit' },
  { label: '%', value: 'percent', type: 'utility', ariaLabel: 'Convert current value to percent' },
  { label: '÷', value: 'divide', type: 'operator', ariaLabel: 'Divide' },
  { label: '7', value: '7', type: 'digit', ariaLabel: 'Seven' },
  { label: '8', value: '8', type: 'digit', ariaLabel: 'Eight' },
  { label: '9', value: '9', type: 'digit', ariaLabel: 'Nine' },
  { label: '×', value: 'multiply', type: 'operator', ariaLabel: 'Multiply' },
  { label: '4', value: '4', type: 'digit', ariaLabel: 'Four' },
  { label: '5', value: '5', type: 'digit', ariaLabel: 'Five' },
  { label: '6', value: '6', type: 'digit', ariaLabel: 'Six' },
  { label: '−', value: 'subtract', type: 'operator', ariaLabel: 'Subtract' },
  { label: '1', value: '1', type: 'digit', ariaLabel: 'One' },
  { label: '2', value: '2', type: 'digit', ariaLabel: 'Two' },
  { label: '3', value: '3', type: 'digit', ariaLabel: 'Three' },
  { label: '+', value: 'add', type: 'operator', ariaLabel: 'Add' },
  { label: '0', value: '0', type: 'digit', ariaLabel: 'Zero', span: 'double' },
  { label: '.', value: '.', type: 'decimal', ariaLabel: 'Decimal point' },
  { label: '=', value: 'equals', type: 'equals', ariaLabel: 'Calculate result' },
]
