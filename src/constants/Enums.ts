const EProperty_Type:Record<string, string> = {
  'condo': 'Condo',
  'single_family': 'Single Family'
}

const EProperty_Type2:Record<string, string> = {
  'house-duplex': 'Single Family',
  'condo-apt': 'Condo & Apts.'
}

const EProperty_Status:Record<string, string> = {
  'for_sale': 'For Sale',
  'pending': 'Pending',
  'sold': 'Sold'
}

const toBeExported:{ [key:string]:Record<string, string> } = {
  EProperty_Type,
  EProperty_Status,
  EProperty_Type2
};

export default toBeExported;