import ItemDetails from './ItemDetails.vue';

import databases from '~api/databases';


jest.mock('~api/databases', () => ({
  get: jest.fn((id) => ({ id })),
}));

describe('ItemDetails', () => {
  let cmp;
  let context;

  beforeEach(() => {
    cmp = ItemDetails;
  });

  describe('#data', () => {
    it('should provide initial data', () => {
      expect(cmp.data()).toEqual({
        isDialogOpened: false,
        isReconfDialogOpened: false,
        loading: false,
        hidePassword: true,
        editingItem: null,
        localItem: null,

        visibilityIcon: {
          on: 'test-file-stub',
          off: 'test-file-stub',
        },
      });
    });
  });

  describe('#methods', () => {
    describe('openReconfigureDialog', () => {
      it('should set isReconfDialogOpened to true', () => {
        context = { isReconfDialogOpened: false };
        cmp.methods.openReconfigureDialog.call(context);

        expect(context.isReconfDialogOpened).toBe(true);
      });
    });

    describe('#openEditDialog()', () => {
      it('should set isDialogOpened to true', () => {
        context = { isDialogOpened: false };
        cmp.methods.openEditDialog.call(context);

        expect(context.isDialogOpened).toBe(true);
      });
    });

    describe('#load()', () => {
      beforeEach(async () => {
        context = { item: 'xxx', localItem: null };
        await cmp.methods.load.call(context);
      });

      it('should call datanbases.get with proper id', () => {
        expect(databases.get).toHaveBeenCalledWith('xxx');
      });

      it('should set localItem with returned value', () => {
        expect(context.localItem).toEqual({ id: 'xxx' });
      });
    });

    describe('#onBack()', () => {
      it('should $emit "closed"', () => {
        context = { $emit: jest.fn() };

        cmp.methods.onBack.call(context);

        expect(context.$emit).toHaveBeenCalledWith('closed');
      });
    });

    describe('#redirect()', () => {
      it('should $emit "redirect" with proper id', () => {
        context = { emit: jest.fn() };

        cmp.methods.redirect.call(context, 'foo');

        expect(context.emit).toHaveBeenCalledWith({ name: 'redirect', value: 'foo' });
      });
    });
  });

  describe('#filters', () => {
    describe('#ddmmyyyy', () => {
      it.each([
        ['October 19, 1975 23:15:30 GMT+11:00', '19/10/1975'],
        ['January 3, 2020 23:15:30 GMT+11:00', '03/01/2020'],
      ])('should format %j as %j', (d, f) => {
        expect(cmp.filters.ddmmyyyy(new Date(d))).toBe(f);
      });
    });
  });

  describe('#created', () => {
    it('should call #load()', () => {
      context = {
        load: jest.fn(),
      };

      cmp.created.call(context);

      expect(context.load).toHaveBeenCalled();
    });
  });
});
