import client from './client'

export const login    = (payload: { username: string; password: string }) =>
  client.post('/auth/login', payload)

export const register = (payload: { username: string; password: string }) =>
  client.post('/auth/register', payload)

export const logout   = () => client.post('/auth/logout', {})
