import ActivateDialog from './ActivateDialog.vue';

import databases from '~api/databases';


jest.mock('~api/databases', () => ({
  activate: jest.fn((id, obj) => ({ id, ...obj })),
}));

describe('ActivateDialog', () => {
  let cmp;
  let context;

  beforeEach(() => {
    cmp = ActivateDialog;
  });

  describe('#data', () => {
    it('should provide initial data', () => {
      expect(cmp.data()).toEqual({
        dialogOpened: false,
        saving: false,
        form: {
          credentials: {
            name: '',
            host: '',
            username: '',
            password: '',
          },
          workload: 'small',
        },
      });
    });
  });

  describe('#computed', () => {
    describe('#allowSaving', () => {
      it.each([
        [
          true,
          {
            credentials: {
              username: 'username',
              password: 'password',
              host: 'host',
            },
          },
        ],
        [
          false,
          {
            credentials: {
              username: '',
              password: '',
              host: '',
              name: 'DB',
            },
          },
        ],
      ])('returns %s', (expected, form) => {
        expect(cmp.computed.allowSaving({ form })).toBe(expected);
      });
    });
  });

  describe('#methods', () => {
    describe('#close()', () => {
      beforeEach(() => {
        context = {
          dialogOpened: true,
          form: {},
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

      it('reinitializes the form', () => {
        expect(context.form).toEqual({
          credentials: {
            name: '',
            host: '',
            username: '',
            password: '',
          },
          workload: 'small',
        });
      });
    });

    describe('#save()', () => {
      beforeEach(async () => {
        context = {
          $emit: jest.fn(),
          close: jest.fn(),
          saving: true,

          item: {
            id: 'DB-123',
          },

          form: {
            id: '...',
            name: 'some DB',
            workload: 'large',
            credentials: { 1: 2 },
          },
        };

        await cmp.methods.save.call(context);
      });

      it('should call activate api', () => {
        expect(databases.activate).toHaveBeenCalledWith(
          'DB-123',
          {
            workload: 'large',
            credentials: { 1: 2 },
          },
        );
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
          item: {},
        };

        cmp.watch.value.handler.call(context, value);

        expect(context.dialogOpened).toBe(value);
      });

      it.each([
        [
          {
            id: 'DB-1',
            workload: 'large',
          },
          {
            id: 'DB-1',
            workload: 'large',
            credentials: {
              name: '',
              host: '',
              username: '',
              password: '',
            },
          },
        ],
        [
          {
            name: 'db',
            credentials: {
              random: 'stuff',
            },
          },
          {
            name: 'db',
            credentials: {
              random: 'stuff',
            },
          },
        ],
      ])('should set dialogOpen value', (item, form) => {
        context = {
          dialogOpened: false,
          form: null,
          item,
        };

        cmp.watch.value.handler.call(context, true);

        expect(context.form).toEqual(form);
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
