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
        dialogOpened: false,
        acceptTermsAndConds: false,
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
            subject: 'foo',
            description: 'bar',
          },
        };

        await cmp.methods.save.call(context);
      });

      it('should call reconfigure api', () => {
        expect(databases.reconfigure).toHaveBeenCalledWith(
          'xxx',
          { case: { subject: 'foo', description: 'bar' } },
        );
      });

      it('should emit "saved" event', () => {
        expect(context.$emit).toHaveBeenCalledWith(
          'saved',
          {
            id: 'xxx',
            case: { subject: 'foo', description: 'bar' },
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
      let setContext;
      let call;

      beforeEach(() => {
        setContext = (mode, item) => {
          context = {
            mode,
            item,
            dialogOpened: null,
            form: null,
          };
        };

        call = (...args) => (cmp.watch.value.handler).call(context, ...args);
      });

      it.each([
        [false, 'create', null, ['form', 'toBe', null]],
        [true, 'create', null, ['form', 'toBe', null]],
        [true, 'edit', null, ['form', 'toBe', null]],
        [true, 'edit', { foo: 'bar' }, ['form', 'toEqual', { foo: 'bar' }]],

        [false, 'create', null, ['dialogOpened', 'toBe', false]],
        [true, 'create', null, ['dialogOpened', 'toBe', true]],
        [true, 'edit', null, ['dialogOpened', 'toBe', true]],
        [true, 'edit', { foo: 'dialogOpened' }, ['dialogOpened', 'toBe', true]],
      ])(
        'When mode=%j, item=% should "%j"',
        (val, mode, item, spec) => {
          const [property, satisfies, condition] = spec;

          setContext(mode, item);
          call(val);

          expect(context[property])[satisfies](condition);
        },
      );
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
