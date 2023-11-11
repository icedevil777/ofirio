import ArrayIncludes from '@/bootstrap/ArrayIncludes';
import AxiosBaseURL from '@/bootstrap/AxiosBaseURL';
import CSRFTokenBoostrap from '@/bootstrap/CSRFToken';
import AccountInit from '@/bootstrap/AccountInit';

export default async function () {
  await Promise.all([
    ArrayIncludes(),
    AxiosBaseURL()
  ]);
  await CSRFTokenBoostrap();
  await AccountInit();
}