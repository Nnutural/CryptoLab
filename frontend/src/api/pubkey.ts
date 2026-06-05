import client from './client'

export const rsaKeygen   = (payload: unknown) => client.post('/pubkey/rsa/keygen', payload)
export const rsaEncrypt  = (payload: unknown) => client.post('/pubkey/rsa/encrypt', payload)
export const rsaDecrypt  = (payload: unknown) => client.post('/pubkey/rsa/decrypt', payload)
export const rsaSign     = (payload: unknown) => client.post('/pubkey/rsa/sign',    payload)
export const rsaVerify   = (payload: unknown) => client.post('/pubkey/rsa/verify',  payload)

export const eccKeygen   = (payload: unknown) => client.post('/pubkey/ecc/keygen', payload)
export const ecdsaSign   = (payload: unknown) => client.post('/pubkey/ecdsa/sign', payload)
export const ecdsaVerify = (payload: unknown) => client.post('/pubkey/ecdsa/verify', payload)
