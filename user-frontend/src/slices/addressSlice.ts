import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AddressState {
  addresses: any[];
}

const initialState: AddressState = {
  addresses: [],
};

const addressSlice = createSlice({
  name: 'address',
  initialState,
  reducers: {
    setAddresses: (state, action: PayloadAction<any[]>) => {
      state.addresses = action.payload;
    },
    addAddress: (state, action: PayloadAction<any>) => {
      state.addresses.push(action.payload);
    },
    deleteAddress: (state, action: PayloadAction<number>) => {
      state.addresses = state.addresses.filter((_, idx) => idx !== action.payload);
    },
  },
});

export const { setAddresses, addAddress, deleteAddress } = addressSlice.actions;
export default addressSlice.reducer;
