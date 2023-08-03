import * as yup from 'yup';


/***
 *               _                     _       
 *         /\   | |                   (_)      
 *        /  \  | |_  ___   _ __ ___   _   ___ 
 *       / /\ \ | __|/ _ \ | '_ ` _ \ | | / __|
 *      / ____ \| |_| (_) || | | | | || || (__ 
 *     /_/    \_\\__|\___/ |_| |_| |_||_| \___|
 *                                             
 *                                             
 */

export const VEmail = yup.string().typeError('Email must be valid').email('Email must be valid').required('Email is required');

export const VPassword = yup.string().typeError('Password must be valid')
                            .min(6, 'Minimal password length is 6')
                            .matches(/\d/, 'Password must contain at least 1 digit')
                            .matches(/[a-zA-Z]/, 'Password must contain at least 1 character');

export const VFullName = yup
  .string()
  .required('Name is required')
  .typeError('Name is required')
  .matches(/^([^0-9]*)$/g, 'Must not contain digits')
  .matches(/^[a-zA-Z]{2,40}(?: +[a-zA-Z]{2,40})+$/g, 'Must contain at least two words');

const phoneRegExp = /^((\+\d{1,3}(-| )?\(?\d\)?(-| )?\d{1,3})|(\(?\d{2,3}\)?))(-| )?(\d{3,4})(-| )?(\d{4})(( x| ext)\d{1,5}){0,1}$/;
export const VPhoneNumber = yup.string().typeError('Phone number is required').required('Phone number is required').matches(phoneRegExp, 'Phone must be valid');

export const VRequestMessage = yup.string().typeError('Request text cannot be empty').min(5, 'Request text may not be blank');


/***
 *       _____  _                         
 *      / ____|| |                        
 *     | (___  | |__    __ _  _ __    ___ 
 *      \___ \ | '_ \  / _` || '_ \  / _ \
 *      ____) || | | || (_| || |_) ||  __/
 *     |_____/ |_| |_| \__,_|| .__/  \___|
 *                           | |          
 *                           |_|          
 */

export const VAuthData = yup.object().shape({
  email: VEmail.required('Email is required'),
  password: VPassword.required('Password is required')
});

export const VAgents = yup.object().shape({
  full_name: VFullName,
  email: VEmail,
  phone: VPhoneNumber,
  request: VRequestMessage
});

export const VContactUs = yup.object().shape({
  full_name: VFullName,
  email: VEmail,
  message: VRequestMessage
});