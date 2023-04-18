import ReconfDialog from './ReconfDialog.vue';

import databases from '~api/databases';


jest.mock('~api/databases', () => ({
  reconfigure: jest.fn((id, obj) => ({ id, ...obj })),
}));

describe('ReconfDialog', () => {
  let cmp;
  let context;

  beforeEach(() => {
    cmp = ReconfDialog;
  });

  describe('#data', () => {
    it('should provide initial data', () => {
      expect(cmp.data()).toEqual({
        errorText: null,
        dialogOpened: false,
        acceptTermsAndConds: false,
        saving: false,
        form: {
          subject: '',
          description: '',
        },
      });
    });
  });

  describe('#methods', () => {
    describe('#close()', () => {
      beforeEach(() => {
        context = {
          dialogOpened: true,
          form: { foo: 'bar' },
          $emit: jest.fn(),
        };

        cmp.methods.close.call(context);
      });

      it.each([
        [['dialogOpened', 'toBe', false]],
        [['form', 'toEqual', { subject: '', description: '' }]],
      ])(
        'should "%j"',
        (spec) => {
          const [property, satisfies, condition] = spec;

          expect(context[property])[satisfies](condition);
        },
      );
    });

    describe('#save()', () => {
      beforeEach(async () => {
        context = {
          $emit: jest.fn(),
          close: jest.fn(),

          item: {
            id: 'xxx',
          },

          form: {
            subject: 'regenerate_access',
            description: 'bar',
          },
        };

        await cmp.methods.save.call(context);
      });

      it('should call reconfigure api', () => {
        expect(databases.reconfigure).toHaveBeenCalledWith(
          'xxx',
          { details: 'Regenerate access\n\nbar', action: 'update' },
        );
      });

      it('should emit "saved" event', () => {
        expect(context.$emit).toHaveBeenCalledWith(
          'saved',
          {
            id: 'xxx',
            details: 'Regenerate access\n\nbar',
            action: 'update',
          },
        );
      });

      it('should call #close', () => {
        expect(context.close).toHaveBeenCalled();
      });
    });
  });

  describe('#watch', () => {
    describe('#value()', () => {
      it('should set dialogOpen value', () => {
        context = {
          dialogOpened: false,
        };

        cmp.watch.value.handler.call(context, true);

        expect(context.dialogOpened).toBe(true);
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
