import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

/****************************************
 **************** Store *****************
 ****************************************/
const store = new Vuex.Store({
  state: {
    currentUser: {
    }
  },
  getters: {
    isStaffUser: function(state) {
      return true === state.currentUser.is_staff;
    },
    isSuperUser: function(state) {
      return true === state.currentUser.is_superuser;
    },
    isStaffOrSuperUser: function(state) {
      return (
        true === (state.currentUser.is_staff || state.currentUser.is_superuser)
      );
    },
    isRacerUser: function(state) {
      return true === state.currentUser.is_racer;
    },
    isStaffPromotorUser: function(state) {
      return true === state.currentUser.is_staff_promotor;
    },
    isLoadedUser: function(state) {
      return !!state.currentUser.id;
    },
    userDisplayName: function(state) {
      if(state.currentUser.id) {
        var name = (state.currentUser.firstname || state.currentUser.username);
        return name.charAt(0).toUpperCase() + name.slice(1);
      }
    }
  }
});

export default store;
