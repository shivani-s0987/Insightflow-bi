import axios from 'axios';
export const api=axios.create({baseURL:import.meta.env.VITE_API_URL||'http://localhost:8000/api/v1/',withCredentials:true,timeout:20000});
api.interceptors.request.use(async config=>{if(['post','put','patch','delete'].includes((config.method||'').toLowerCase())){const cookie=document.cookie.split('; ').find(v=>v.startsWith('csrftoken='))?.split('=')[1];if(cookie)config.headers['X-CSRFToken']=decodeURIComponent(cookie);}return config;});
export function errorMessage(error:unknown){if(axios.isAxiosError(error)){const data=error.response?.data as {detail?:string;code?:string}|undefined;return data?.detail||data?.code||error.message||'Request failed. Please try again.';}return 'Something went wrong. Please try again.';}
export type Workspace={id:number;name:string;slug:string;role:string};
export type Dataset={id:number;name:string;format:string;rows:number;columns:number;column_names:{name:string;dtype:string}[];created_at?:string};
