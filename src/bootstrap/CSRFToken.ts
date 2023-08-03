import CSRFTokenService from '@/services/CSRFToken.service';

export default async function () {
  await CSRFTokenService.refreshCSRFToken();
}