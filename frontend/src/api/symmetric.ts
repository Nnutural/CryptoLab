import client from './client'

export const symmetricEncrypt = (algo: string, payload: unknown) =>
  client.post(`/symmetric/${algo}/encrypt`, payload)

export const symmetricDecrypt = (algo: string, payload: unknown) =>
  client.post(`/symmetric/${algo}/decrypt`, payload)
