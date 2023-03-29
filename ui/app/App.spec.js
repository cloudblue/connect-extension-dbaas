import App from './App.vue';


describe('App', () => {
  let cmp;
  let context;

  beforeEach(() => {
    cmp = App;
  });

  describe('#data', () => {
    it('should provide initial data', () => {
      expect(cmp.data()).toEqual({
        active: 'list',
        item: null,
      });
    });
  });

  describe('#methods', () => {
    describe('#openDetails()', () => {
      let setContext;
      let call;

      beforeEach(() => {
        setContext = () => {
          context = {
            item: null,
            active: null,
          };
        };

        call = (...args) => cmp.methods.openDetails.call(context, ...args);
      });

      it.each([
        [['active', 'toEqual', 'details']],
        [['item', 'toEqual', 'foo']],
      ])(
        'should "%j"',
        (spec) => {
          const [property, satisfies, condition] = spec;

          setContext();
          call({ id: 'foo' });

          const assertion = expect(context[property]);

          assertion[satisfies](condition);
        },
      );
    });

    describe('#openList()', () => {
      let setContext;
      let call;

      beforeEach(() => {
        setContext = () => {
          context = {
            item: 'foo',
            active: 'bar',
          };
        };

        call = (...args) => cmp.methods.openList.call(context, ...args);
      });

      it.each([
        [['item', 'toEqual', null]],
        [['active', 'toBe', 'list']],
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
  });
});
