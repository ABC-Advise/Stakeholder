export function removeNonNumeric(value: string) {
  return value.replace(/\D/g, ''); // Remove todos os caracteres não numéricos
}
