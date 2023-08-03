import API from './api';
import { APP_DEFAULT_SMTH_BAD_FROM_SERVER } from '@/constants/DefaultMessages';

export default {

  async getMlsInfo() {
    const [res, err] = await API.getMlsInfo();
    if (err) {
      console.error(err);
      throw APP_DEFAULT_SMTH_BAD_FROM_SERVER;
    }

    return res.data.update_onsite;
  }

}