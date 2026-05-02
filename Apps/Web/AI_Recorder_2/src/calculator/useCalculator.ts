import { useCallback, useEffect, useMemo, useState } from 'react'
import { CalculatorKeyValue, Operator, operatorSymbols } from './calculatorData'

const MAX_INPUT_DIGITS = 16

type CalculationResult = {
  value: number
  errorMessage?: string
}

type LastOperation = {
  operator: Operator
  rightOperand: number
}

type CalculatorState = {
  displayValue: string
  expression: string
  statusText: string
  storedValue: number | null
  pendingOperator: Operator | null
  waitingForNextValue: boolean
  errorMessage: string | null
  lastOperation: LastOperation | null
  hasEvaluated: boolean
}

const initialState: CalculatorState = {
  displayValue: '0',
  expression: '',
  statusText: 'Ready',
  storedValue: null,
  pendingOperator: null,
  waitingForNextValue: false,
  errorMessage: null,
  lastOperation: null,
  hasEvaluated: false,
}

function toNumber(value: string) {
  return Number(value)
}

function countDigits(value: string) {
  return value.replace(/[^0-9]/g, '').length
}

function formatNumber(value: number) {
  if (!Number.isFinite(value)) {
    return '0'
  }

  if (Object.is(value, -0)) {
    return '0'
  }

  const absoluteValue = Math.abs(value)
  const formattedValue = absoluteValue >= 1e12 || (absoluteValue > 0 && absoluteValue < 1e-6)
    ? value.toExponential(8)
    : Number(value.toFixed(10)).toString()

  return formattedValue.length > 18 ? value.toPrecision(12).replace(/\.0+e/, 'e') : formattedValue
}

function calculate(leftOperand: number, rightOperand: number, operator: Operator): CalculationResult {
  switch (operator) {
    case 'add':
      return { value: leftOperand + rightOperand }
    case 'subtract':
      return { value: leftOperand - rightOperand }
    case 'multiply':
      return { value: leftOperand * rightOperand }
    case 'divide':
      if (rightOperand === 0) {
        return { value: 0, errorMessage: 'Cannot divide by zero' }
      }
      return { value: leftOperand / rightOperand }
    default:
      return { value: rightOperand }
  }
}

function errorState(message: string, expression: string): CalculatorState {
  return {
    ...initialState,
    displayValue: 'Error',
    expression,
    statusText: 'Invalid calculation',
    errorMessage: message,
  }
}

function getOperationExpression(leftOperand: number, operator: Operator, rightOperand?: number, suffix = '') {
  const parts = [formatNumber(leftOperand), operatorSymbols[operator]]

  if (rightOperand !== undefined) {
    parts.push(formatNumber(rightOperand))
  }

  return `${parts.join(' ')}${suffix}`
}

function inputDigit(state: CalculatorState, digit: string): CalculatorState {
  if (state.errorMessage || (state.hasEvaluated && !state.pendingOperator)) {
    return {
      ...initialState,
      displayValue: digit,
      statusText: 'Entering number',
    }
  }

  if (state.waitingForNextValue) {
    return {
      ...state,
      displayValue: digit,
      waitingForNextValue: false,
      errorMessage: null,
      statusText: 'Entering number',
    }
  }

  if (countDigits(state.displayValue) >= MAX_INPUT_DIGITS) {
    return {
      ...state,
      statusText: 'Maximum display length reached',
    }
  }

  return {
    ...state,
    displayValue: state.displayValue === '0' ? digit : `${state.displayValue}${digit}`,
    statusText: 'Entering number',
    hasEvaluated: false,
  }
}

function inputDecimal(state: CalculatorState): CalculatorState {
  if (state.errorMessage || (state.hasEvaluated && !state.pendingOperator)) {
    return {
      ...initialState,
      displayValue: '0.',
      statusText: 'Entering decimal',
    }
  }

  if (state.waitingForNextValue) {
    return {
      ...state,
      displayValue: '0.',
      waitingForNextValue: false,
      statusText: 'Entering decimal',
    }
  }

  if (state.displayValue.includes('.')) {
    return state
  }

  return {
    ...state,
    displayValue: `${state.displayValue}.`,
    statusText: 'Entering decimal',
  }
}

function clearCalculator(): CalculatorState {
  return initialState
}

function backspace(state: CalculatorState): CalculatorState {
  if (state.errorMessage) {
    return initialState
  }

  if (state.waitingForNextValue || state.hasEvaluated) {
    return {
      ...state,
      displayValue: '0',
      waitingForNextValue: false,
      hasEvaluated: false,
      statusText: 'Cleared current entry',
    }
  }

  const nextValue = state.displayValue.slice(0, -1)

  return {
    ...state,
    displayValue: nextValue && nextValue !== '-' ? nextValue : '0',
    statusText: 'Deleted last digit',
  }
}

function percent(state: CalculatorState): CalculatorState {
  if (state.errorMessage) {
    return initialState
  }

  const currentValue = toNumber(state.displayValue)
  const nextDisplayValue = formatNumber(currentValue / 100)

  return {
    ...state,
    displayValue: nextDisplayValue,
    waitingForNextValue: false,
    hasEvaluated: false,
    statusText: 'Converted to percent',
  }
}

function chooseOperator(state: CalculatorState, operator: Operator): CalculatorState {
  if (state.errorMessage) {
    return {
      ...initialState,
      pendingOperator: operator,
      expression: `0 ${operatorSymbols[operator]}`,
      waitingForNextValue: true,
    }
  }

  const currentValue = toNumber(state.displayValue)

  if (state.storedValue === null) {
    return {
      ...state,
      storedValue: currentValue,
      pendingOperator: operator,
      expression: getOperationExpression(currentValue, operator),
      waitingForNextValue: true,
      errorMessage: null,
      hasEvaluated: false,
      lastOperation: null,
      statusText: 'Operator selected',
    }
  }

  if (state.waitingForNextValue) {
    return {
      ...state,
      pendingOperator: operator,
      expression: getOperationExpression(state.storedValue, operator),
      statusText: 'Operator changed',
    }
  }

  if (!state.pendingOperator) {
    return {
      ...state,
      pendingOperator: operator,
      expression: getOperationExpression(currentValue, operator),
      storedValue: currentValue,
      waitingForNextValue: true,
      lastOperation: null,
      statusText: 'Operator selected',
    }
  }

  const result = calculate(state.storedValue, currentValue, state.pendingOperator)

  if (result.errorMessage) {
    return errorState(result.errorMessage, getOperationExpression(state.storedValue, state.pendingOperator, currentValue, ' ='))
  }

  const displayValue = formatNumber(result.value)

  return {
    ...state,
    displayValue,
    storedValue: result.value,
    pendingOperator: operator,
    expression: getOperationExpression(result.value, operator),
    waitingForNextValue: true,
    lastOperation: null,
    hasEvaluated: false,
    statusText: 'Intermediate result ready',
  }
}

function equals(state: CalculatorState): CalculatorState {
  if (state.errorMessage) {
    return initialState
  }

  const currentValue = toNumber(state.displayValue)

  if (state.pendingOperator && state.storedValue !== null) {
    if (state.waitingForNextValue) {
      return {
        ...state,
        statusText: 'Enter the next number to calculate',
      }
    }

    const result = calculate(state.storedValue, currentValue, state.pendingOperator)
    const expression = getOperationExpression(state.storedValue, state.pendingOperator, currentValue, ' =')

    if (result.errorMessage) {
      return errorState(result.errorMessage, expression)
    }

    return {
      ...state,
      displayValue: formatNumber(result.value),
      expression,
      storedValue: null,
      pendingOperator: null,
      waitingForNextValue: true,
      lastOperation: {
        operator: state.pendingOperator,
        rightOperand: currentValue,
      },
      hasEvaluated: true,
      statusText: 'Result displayed',
    }
  }

  if (state.hasEvaluated && state.lastOperation) {
    const result = calculate(currentValue, state.lastOperation.rightOperand, state.lastOperation.operator)
    const expression = getOperationExpression(currentValue, state.lastOperation.operator, state.lastOperation.rightOperand, ' =')

    if (result.errorMessage) {
      return errorState(result.errorMessage, expression)
    }

    return {
      ...state,
      displayValue: formatNumber(result.value),
      expression,
      waitingForNextValue: true,
      statusText: 'Repeated operation applied',
    }
  }

  return {
    ...state,
    statusText: 'No pending operation',
  }
}

function reduceCalculatorState(state: CalculatorState, value: CalculatorKeyValue): CalculatorState {
  if (/^[0-9]$/.test(value)) {
    return inputDigit(state, value)
  }

  if (value === '.') {
    return inputDecimal(state)
  }

  if (value === 'clear') {
    return clearCalculator()
  }

  if (value === 'backspace') {
    return backspace(state)
  }

  if (value === 'percent') {
    return percent(state)
  }

  if (value === 'equals') {
    return equals(state)
  }

  return chooseOperator(state, value as Operator)
}

function keyboardValue(key: string): CalculatorKeyValue | null {
  if (/^[0-9]$/.test(key)) {
    return key as CalculatorKeyValue
  }

  const keyboardMap: Record<string, CalculatorKeyValue> = {
    '.': '.',
    ',': '.',
    '+': 'add',
    '-': 'subtract',
    '*': 'multiply',
    'x': 'multiply',
    'X': 'multiply',
    '/': 'divide',
    '%': 'percent',
    '=': 'equals',
    Enter: 'equals',
    Backspace: 'backspace',
    Delete: 'backspace',
    Escape: 'clear',
    c: 'clear',
    C: 'clear',
  }

  return keyboardMap[key] ?? null
}

export function useCalculator() {
  const [state, setState] = useState<CalculatorState>(initialState)

  const pressKey = useCallback((value: CalculatorKeyValue) => {
    setState((currentState) => reduceCalculatorState(currentState, value))
  }, [])

  useEffect(() => {
    const handleKeyboardInput = (event: KeyboardEvent) => {
      const value = keyboardValue(event.key)

      if (!value) {
        return
      }

      event.preventDefault()
      pressKey(value)
    }

    window.addEventListener('keydown', handleKeyboardInput)

    return () => window.removeEventListener('keydown', handleKeyboardInput)
  }, [pressKey])

  return useMemo(() => ({
    ...state,
    pressKey,
  }), [pressKey, state])
}
