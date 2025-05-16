export const formatCpfCnpj = (value: string) => {
  value = value.replace(/\D/g, ''); // Remove all non-digit characters

  if (value.length <= 11) {
    // CPF format: 000.000.000-00
    return value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  } else {
    // CNPJ format: 00.000.000/0000-00
    return value.replace(
      /(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/,
      '$1.$2.$3/$4-$5'
    );
  }
};
