import CreateEditDialog, {
  initialForm,
} from './CreateEditDialog.vue';

import databases from '~api/databases';


jest.mock('~api/databases', () => ({
  create: jest.fn(),
  update: jest.fn(),
}));

jest.mock('~api/regions', () => ({
  list: jest.fn(() => ['eu', 'us']),
}));

jest.mock('~api/context', () => ({
  get: jest.fn(() => ({ account: { id: 'foo' } })),
}));

jest.mock('~api/account-users', () => ({
  list: jest.fn(id => [{ id }]),
}));



describe('CreateEditDialog', () => {
  let cmp;
  let context;

  beforeEach(() => {
    cmp = CreateEditDialog;
  });

  describe('#data', () => {
    it('should provide initial data', () => {
      expect(cmp.data()).toEqual({
        dialogOpened: false,
        acceptTermsAndConds: false,
        saving: false,
        regions: [],
        users: [],
        form: initialForm(),
      });
    });
  });

  describe('#computed', () => {
    describe('#isEdit', () => {
      let setContext;

      beforeEach(() => {
        setContext = (item) => {
          context = { item };
        };
      });

      it.each([
        [{ id: 'foo' }, ['toBe', true]],
        [null, ['toBe', false]],
      ])(
        'When item should "%j"',
        (item, spec) => {
          const [satisfies, condition] = spec;

          setContext(item);

          const assertion = expect(cmp.computed.isEdit(context));

          assertion[satisfies](condition);
        },
      );
    });

    describe('#allowSaving', () => {
      let setContext;

      beforeEach(() => {
        setContext = (isEdit, acceptTermsAndConds, name, description, contact, region) => {
          context = {
            isEdit,
            acceptTermsAndConds,

            form: {
              name,
              description,

              tech_contact: {
                id: contact,
              },

              region: {
                id: region,
              },
            },
          };
        };
      });

      it.each([
        [false, true, 'name', 'description', 'contact', 'region', ['toBe', true]],
        [false, false, null, null, null, null, ['toBe', false]],
        [false, true, null, null, null, null, ['toBe', false]],
        [false, true, 'name', null, null, null, ['toBe', false]],
        [false, true, null, 'description', null, null, ['toBe', false]],
        [false, true, 'name', 'description', 'contact', null, ['toBe', false]],
        [false, false, 'name', 'description', 'contact', 'region', ['toBe', false]],
        [false, false, null, 'description', 'contact', 'region', ['toBe', false]],
        [false, false, null, null, null, 'region', ['toBe', false]],

        [true, false, 'name', 'description', 'contact', null, ['toBe', true]],
        [true, false, null, null, 'contact', null, ['toBe', false]],
        [true, false, null, null, null, null, ['toBe', false]],
        [true, false, 'name', null, null, null, ['toBe', false]],
      ])(
        'When isEdit=%j, acceptTermsAndConds=%j, name=%j, contact=%j, region=%j should "%j"',
        (isEdit, acceptTermsAndConds, name, description, contact, region, spec) => {
          const [satisfies, condition] = spec;

          setContext(isEdit, acceptTermsAndConds, name, description, contact, region);

          expect(cmp.computed.allowSaving(context))[satisfies](condition);
        },
      );
    });
  });

  describe('#methods', () => {
    describe('#close()', () => {
      let setContext;
      let call;

      beforeEach(() => {
        setContext = () => {
          context = {
            dialogOpened: true,
            form: { name: 'foobar' },
            users: ['foo', 'bar'],
            regions: ['fuz', 'buz'],
            $emit: jest.fn(),
          };
        };

        call = () => cmp.methods.close.call(context);
      });

      it.each([
        [['dialogOpened', 'toBe', false]],
        [['form', 'toEqual', initialForm()]],
        [['users', 'toEqual', []]],
        [['regions', 'toEqual', []]],
      ])(
        'should "%j"',
        (spec) => {
          const [property, satisfies, condition] = spec;

          setContext();
          call();

          const assertion = expect(context[property]);

          assertion[satisfies](condition);
        },
      );
    });

    describe('#save()', () => {
      let setContext;
      let call;

      beforeEach(() => {
        setContext = (isEdit) => {
          context = {
            databases,
            isEdit,
            $emit: jest.fn(),
            close: jest.fn(),
            saving: false,
            item: { id: 'foo' },
            form: {
              name: 'foobar',
              description: 'Foo bar',
              tech_contact: { id: 'buz' },
              workload: 'high',
              region: { id: 'fuz' },
            },
          };
        };

        call = () => cmp.methods.save.call(context);
      });

      it('should emit proper event', async () => {
        setContext(true);
        await call();

        expect(context.$emit).toHaveBeenCalledWith('saved');
      });

      it('should close dialog', async () => {
        setContext(true);
        await call();

        expect(context.close).toHaveBeenCalled();
      });

      it('should call databases.update with proper args on edit', async () => {
        setContext(true);
        await call();

        expect(databases.update).toHaveBeenCalledWith('foo', {
          name: 'foobar',
          description: 'Foo bar',
          tech_contact: { id: 'buz' },
        });
      });

      it('should call databases.create with proper args on create', async () => {
        setContext(false);
        await call();

        expect(databases.create).toHaveBeenCalledWith({
          name: 'foobar',
          description: 'Foo bar',
          tech_contact: { id: 'buz' },
          workload: 'high',
          region: { id: 'fuz' },
        });
      });
    });
  });

  describe('#watch', () => {
    describe('#value()', () => {
      let setContext;
      let call;

      beforeEach(() => {
        setContext = (item) => {
          context = {
            item,
            form: { fuz: 'buz' },
            regions: [],
            users: [],
            dialogOpened: null,
          };
        };

        call = (...args) => (cmp.watch.value?.handler || cmp.watch.value).call(context, ...args);
      });

      it.each([
        [true, { foo: 'bar' }, ['form', 'toEqual', { foo: 'bar' }]],
        [true, null, ['form', 'toEqual', { fuz: 'buz' }]],
        [true, null, ['regions', 'toEqual', ['eu', 'us']]],
        [true, null, ['users', 'toEqual', [{ id: 'foo' }]]],
        [true, null, ['dialogOpened', 'toBe', true]],
        [false, null, ['regions', 'toEqual', []]],
        [false, null, ['users', 'toEqual', []]],
        [false, null, ['dialogOpened', 'toBe', false]],
      ])(
        'When value=%j, item=%j and  should "%j"',
        async (value, item, spec) => {
          const [property, satisfies, condition] = spec;

          setContext(item);
          await call(value);

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
        [true, true, ['$emit', 'not.toHaveBeenCalled']],
        [true, false, ['$emit', 'toHaveBeenCalledWith', ['input', false]]],
        [false, true, ['$emit', 'toHaveBeenCalledWith', ['input', true]]],
        [false, false, ['$emit', 'not.toHaveBeenCalled']],
      ])(
        'When value should "%j"',
        (value, arg, spec) => {
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
