import API, { TPublic__Client__ContactUs } from './api';
import { APP_DEFAULT_SMTH_BAD_FROM_SERVER } from '@/constants/DefaultMessages';

export default {

  async sendContactUs(data: TPublic__Client__ContactUs) {
    if (!data)
      return false;
    
    const [res, err] = await API.send(data);
    if (err) {
      console.error(err);
      throw APP_DEFAULT_SMTH_BAD_FROM_SERVER;
    }

    return true;
  }

}