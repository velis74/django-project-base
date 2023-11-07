import { FormConsumerApi } from '@velis/dynamicforms';
import { AxiosError } from 'axios';
// eslint-disable-next-line import/no-extraneous-dependencies
import MockAdapter from 'axios-mock-adapter';

import { apiClient } from '../../api-client';

const mock = new MockAdapter(apiClient);

const testUrl = '/account/impersonate';

describe('User Profile', () => {
  afterEach(() => {
    mock.reset();
  });

  it('Impersonate', async () => {
    const consumer = new FormConsumerApi({ url: testUrl, query: { id: 1000 }, useQueryInRetrieveOnly: false });
    // @ts-ignore
    consumer.data = { id: 1000 };
    try {
      await consumer.save();
    } catch (e) {
      expect(((e as AxiosError)?.response?.config.method ?? '')).toBe('put');
    }
  });
});
