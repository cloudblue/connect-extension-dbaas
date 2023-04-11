import DeleteDialog from './DeleteDialog.vue';

import databases from '~api/databases';


jest.mock('~api/databases', () => ({
  delete: jest.fn(),
}));

describe('DeleteDialog', () => {
  let cmp;
  let context;

  beforeEach(() => {
    cmp = DeleteDialog;
  });

  describe('#data', () => {
    it('should provide initial data', () => {
      expect(cmp.data()).toEqual({
        dialogOpened: false,
        saving: false,
      });
    });
  });

  describe('#methods', () => {
    describe('#close()', () => {
      beforeEach(() => {
        context = {
          dialogOpened: true,
          $emit: jest.fn(),
        };

        cmp.methods.close.call(context);
      });

      it('marks dialog as closed', () => {
        expect(context.dialogOpened).toBe(false);
      });

      it('emits `closed` signal', () => {
        expect(context.$emit).toHaveBeenCalledWith('closed');
      });
    });

    describe('#save()', () => {
      beforeEach(async () => {
        context = {
          $emit: jest.fn(),
          close: jest.fn(),
          saving: true,

          item: {
            id: 'DB-456',
          },
        };

        await cmp.methods.save.call(context);
      });

      it('should call delete api', () => {
        expect(databases.delete).toHaveBeenCalledWith('DB-456');
      });

      it('should emit `saved` event', () => {
        expect(context.$emit).toHaveBeenCalledWith('saved');
      });

      it('should call #close', () => {
        expect(context.close).toHaveBeenCalled();
      });

      it('should set saving to false', () => {
        expect(context.saving).toBe(false);
      });
    });
  });

  describe('#watch', () => {
    describe('#value()', () => {
      it.each([true, false])('should set dialogOpen value to %s', (value) => {
        context = {
          dialogOpened: false,
        };

        cmp.watch.value.handler.call(context, value);

        expect(context.dialogOpened).toBe(value);
      });
    });

    describe('#dialogOpened()', () => {
      let setContext;
      let call;

      beforeEach(() => {
        setContext = (value) => {
          context = {
            value,

            $emit: jest.fn(),
          };
        };

        call = (...args) => (cmp.watch.dialogOpened).call(context, ...args);
      });

      it.each([
        ['foo', 'bar', ['$emit', 'toHaveBeenCalledWith', ['input', 'foo']]],
        ['foo', 'foo', ['$emit', 'not.toHaveBeenCalledWith']],
      ])(
        'When argument=%j and value=%j should "%j"',
        (arg, value, spec) => {
          /* eslint-disable-next-line prefer-const */
          let [property, satisfies, condition = undefined] = spec;

          setContext(value);
          call(arg);

          let assertion = expect(context[property]);

          if (/^not\./.test(satisfies)) {
            assertion = assertion.not;
            satisfies = satisfies.replace('not.', '');
          }

          assertion[satisfies](...(condition || []));
        },
      );
    });
  });
});
