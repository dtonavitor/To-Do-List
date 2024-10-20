const server_url = 'http://localhost:5000'

const validateEmail = (email) => {
  const re = new RegExp("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}")
  return re.test(email);
}