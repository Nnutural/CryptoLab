import client from './client'

export const base64 = (op: 'encode' | 'decode', payload: unknown) =>
  client.post(`/encoding/base64/${op}`, payload)

export const utf8 = (op: 'encode' | 'decode', payload: unknown) =>
  client.post(`/encoding/utf8/${op}`, payload)
