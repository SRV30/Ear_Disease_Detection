export function isValidResultPayload(result) {
  if (!result || typeof result !== 'object') return false;
  const required = ['prediction', 'confidence', 'explanation', 'advice'];
  return required.every((k) => Object.prototype.hasOwnProperty.call(result, k));
}
