import PropertyBasisModule from './basis';
import PropertyFinanceModule from './finance';
import PropertyTaxModel from './taxes';
import PropertyHistoryModel from './history';
import PropertySchoolsModel from './schools';

export type PropertyStoreType = {
  Basis: PropertyBasisModule,
  Finance: PropertyFinanceModule,
  Taxes: PropertyTaxModel,
  History: PropertyHistoryModel,
  Schools: PropertySchoolsModel
}

export default function Property(id: string, financialData?: object) {
  const PropertyObject = <PropertyStoreType>{
    Basis: new PropertyBasisModule(),
    Finance: new PropertyFinanceModule(),
    Taxes: new PropertyTaxModel(),
    History: new PropertyHistoryModel(),
    Schools: new PropertySchoolsModel()
  };

  const existPromise = PropertyObject.Basis.init(id);
  existPromise.then(exists => {
    if (!exists)
      return;

    PropertyObject.Finance.init(id, PropertyObject, financialData);
    PropertyObject.Taxes.init(id);
    PropertyObject.History.init(id);
    PropertyObject.Schools.init(id);
  });

  return { PropertyObject, existPromise };
};