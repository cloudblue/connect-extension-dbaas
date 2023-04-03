import ItemsList from './ItemsList.vue';

import databases from '~api/databases';


jest.mock('@cloudblueconnect/material-svg/baseline', () => ({
  googleStorageBaseline: 'storage_icon',
}));

jest.mock('~api/databases', () => ({
  list: jest.fn(() => ['foo', 'bar']),
}));

describe('ItemsList', () => {
  let cmp;
  let context;

  beforeEach(() => {
    cmp = ItemsList;
  });

  describe('#data', () => {
    it('should provide initial data', () => {
      expect(cmp.data()).toEqual({
        dialogOpened: false,
        loading: false,
        list: [],
      });
    });
  });

  describe('#computed', () => {
    describe('#placeholderIcon', () => {
      it('should return icon', () => {
        expect(cmp.computed.placeholderIcon()).toBe('storage_icon');
      });
    });

    describe('#showPlaceholder', () => {
      let setContext;

      beforeEach(() => {
        setContext = (list, loading) => {
          context = { list, loading };
        };
      });

      it.each([
        [null, false, true],
        [[], false, true],
        [['foo'], false, false],
        [null, true, false],
      ])(
        'When list, loading should "%j"',
        (list, loading, condition) => {
          setContext(list, loading);

          expect(cmp.computed.showPlaceholder(context)).toBe(condition);
        },
      );
    });

    describe('#columns', () => {
      it('should return columns list', () => {
        expect(cmp.computed.columns()).toEqual([{
          name: 'DB',
          value: 'name',

          style: {
            width: '300px',
            paddingLeft: '24px',
          },
        }, {
          name: 'Region',
          value: 'region.name',

          style: {
            width: '100px',
          },
        }, {
          name: 'Workload',
          value: 'workload',

          style: {
            width: '100px',
          },
        }, {
          name: 'Description',
          value: 'description',
        }, {
          name: 'Status',
          value: 'status',

          style: {
            width: '120px',
            paddingLeft: '24px',
          },
        }]);
      });
    });
  });

  describe('#methods', () => {
    describe('#openCreationDialog()', () => {
      it('should set dialogOpened to "true"', () => {
        context = {
          dialogOpened: false,
        };

        cmp.methods.openCreationDialog.call(context);

        expect(context.dialogOpened).toBe(true);
      });
    });

    describe('#load()', () => {
      beforeEach(async () => {
        context = {
          loading: false,
          list: [],
        };

        await cmp.methods.load.call(context);
      });

      it('should fetch list', () => {
        expect(databases.list).toHaveBeenCalled();
      });

      it('should set #list', () => {
        expect(context.list).toEqual(['foo', 'bar']);
      });
    });
  });

  describe('#created', () => {
    it('should call load', () => {
      context = {
        load: jest.fn(),
      };

      cmp.created.call(context);

      expect(context.load).toHaveBeenCalled();
    });
  });
});
