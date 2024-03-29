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
        isActivateDialogOpened: false,
        isDeleteDialogOpened: false,
        loading: false,
        hidePassword: true,
        editingItem: null,
        localItem: null,

        icons: {
          on: 'test-file-stub',
          off: 'test-file-stub',
          copy: 'test-file-stub',
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

    describe('openActivateDialog', () => {
      it('should set isActivateDialogOpened to true', () => {
        context = { isActivateDialogOpened: false };
        cmp.methods.openActivateDialog.call(context);

        expect(context.isActivateDialogOpened).toBe(true);
      });
    });

    describe('openDeleteDialog', () => {
      it('should set isDeleteDialogOpened to true', () => {
        context = { isDeleteDialogOpened: false };
        cmp.methods.openDeleteDialog.call(context);

        expect(context.isDeleteDialogOpened).toBe(true);
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

      it('should call databases.get with proper id', () => {
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
    describe('#ddmmyyyy_HHMM', () => {
      it.each([
        ['October 19, 1975 23:15:30 GMT+11:00', '19/10/1975 12:15'],
        ['January 3, 2020 00:01:30 GMT-10:00', '03/01/2020 10:01'],
      ])('should format %j as %j', (d, f) => {
        expect(cmp.filters.ddmmyyyy_HHMM(new Date(d))).toBe(f);
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
