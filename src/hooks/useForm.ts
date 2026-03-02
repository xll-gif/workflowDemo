import { useState, useCallback, ChangeEvent, FocusEvent } from 'react';

interface UseFormProps<T> {
  initialValues: T;
  validate: (values: T) => Partial<T>;
}

export const useForm = <T extends Record<string, any>>({
  initialValues,
  validate
}: UseFormProps<T>) => {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<T>>({});
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});

  const handleChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
  }, []);

  const handleBlur = useCallback((e: FocusEvent<HTMLInputElement>) => {
    const { name } = e.target;
    setTouched(prev => ({ ...prev, [name]: true }));
    
    // 实时验证
    const validationErrors = validate(values);
    setErrors(prev => ({ ...prev, [name]: validationErrors[name as keyof T] }));
  }, [values, validate]);

  const handleSubmit = useCallback((onSubmit: (values: T) => void) => (e: React.FormEvent) => {
    e.preventDefault();
    
    const validationErrors = validate(values);
    setErrors(validationErrors);
    
    // 标记所有字段为已触摸
    const allTouched = Object.keys(values).reduce((acc, key) => {
      acc[key as keyof T] = true;
      return acc;
    }, {} as Partial<Record<keyof T, boolean>>);
    setTouched(allTouched);
    
    // 如果没有错误则提交
    if (Object.keys(validationErrors).length === 0) {
      onSubmit(values);
    }
  }, [values, validate]);

  const isValid = Object.keys(errors).length === 0;

  return {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    handleSubmit,
    isValid
  };
};
