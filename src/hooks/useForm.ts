import { useState } from 'react';

interface UseFormOptions<T> {
  initialValues: T;
  validations: Record<keyof T, (value: any) => string>;
}

interface UseFormReturn<T> {
  values: T;
  errors: Record<keyof T, string>;
  handleChange: (field: keyof T, value: any) => void;
  validateForm: () => boolean;
  resetForm: () => void;
}

const useForm = <T extends Record<string, any>>(options: UseFormOptions<T>): UseFormReturn<T> => {
  const { initialValues, validations } = options;
  
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Record<keyof T, string>>(
    Object.keys(initialValues).reduce((acc, key) => {
      acc[key as keyof T] = '';
      return acc;
    }, {} as Record<keyof T, string>)
  );

  const handleChange = (field: keyof T, value: any) => {
    setValues(prev => ({ ...prev, [field]: value }));
    
    // 实时验证
    if (validations[field]) {
      const error = validations[field](value);
      setErrors(prev => ({ ...prev, [field]: error }));
    }
  };

  const validateForm = (): boolean => {
    let isValid = true;
    const newErrors = { ...errors };

    Object.keys(validations).forEach((field) => {
      const fieldKey = field as keyof T;
      const error = validations[fieldKey](values[fieldKey]);
      newErrors[fieldKey] = error;
      if (error) {
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  };

  const resetForm = () => {
    setValues(initialValues);
    setErrors(
      Object.keys(initialValues).reduce((acc, key) => {
        acc[key as keyof T] = '';
        return acc;
      }, {} as Record<keyof T, string>)
    );
  };

  return {
    values,
    errors,
    handleChange,
    validateForm,
    resetForm
  };
};

export default useForm;