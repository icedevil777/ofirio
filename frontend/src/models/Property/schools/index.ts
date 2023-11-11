import API from './api';
import VueStore from 'vue-class-store';

export type TProperty_School = {
  id: number,
  lat: number,
  lon: number,
  name: string,
  phone: string,
  grades: {
    range: {
      low: string,
      hight: string
    }
  },
  nces_id: number,
  ratings: {
    parent_rating: number
    great_schools_rating: number
  },
  location: {
    city: string,
    state: string,
    county: string,
    street: string,
    postal_code: string,
    city_slug_id: string
  },
  relevance: string,
  funding_type: string,
  student_count: number,
  greatschools_id: number,
  education_levels: Array<string>,
  distance_in_miles: number,
  student_teacher_ratio: number
}
export type TPropertyDTO_Schools = {
  schools: Array<TProperty_School>
}

@VueStore
export default class PropertySchoolsModel {

  private _dto: TPropertyDTO_Schools | null = null;
  constructor () {}

  public async init(id: string) {
    const [res, err] = await API.calculate({ prop_id: id });

    if (err) {
      if (![200, 400, 404].includes(<number>err.response?.status))
        console.error('Property:Schools :: Invalid response code');
      this._dto = null;
      return false;
    }

    this._dto = res.data;
    return true;
  }

  public get dto() {
    return this._dto;
  }

}