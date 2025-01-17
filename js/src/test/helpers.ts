/**
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import _ from 'lodash';

import {IGoogleAdsApiClient} from '../lib/ads-api-client';

export class MockGoogleAdsApiClient implements IGoogleAdsApiClient {
  customerIds: string[];
  results: Record<string, any[]> = {};

  constructor(customerIds: string[]) {
    this.customerIds = customerIds;
  }

  async getCustomerIds(): Promise<string[]> {
    return new Promise((resolve, reject) => {
      resolve(this.customerIds);
    });
  }

  setupResult(result: any[] | Record<string, any[]>) {
    if (_.isArray(result)) {
      this.results[""] = result;
    } else {
      this.results = result;
    }
  }

  async executeQuery(query: string, customerId: string): Promise<any[]> {
    let result = this.results[customerId] || this.results[""] || [];
    return new Promise((resolve, reject) => {
      resolve(result);
    });
  }

  async *executeQueryStream(
    query: string,
    customerId: string
  ): AsyncGenerator<any[], any, unknown> {
    let result = this.results[customerId] || this.results[""] || [];
    for (const row of result) {
      yield row;
    }
  }
}
