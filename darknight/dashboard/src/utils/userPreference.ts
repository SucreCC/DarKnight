const NUM_USERS_PER_PAGE_KEY = 'darknight-num-users-per-page'
const NUM_USERS_PER_PAGE_DEFAULT = 10

export const getUsersPerPageLimitSize = (): number => {
  const value =
    localStorage.getItem(NUM_USERS_PER_PAGE_KEY) || NUM_USERS_PER_PAGE_DEFAULT.toString()
  return parseInt(value) || NUM_USERS_PER_PAGE_DEFAULT
}

export const setUsersPerPageLimitSize = (value: number | string): void => {
  localStorage.setItem(NUM_USERS_PER_PAGE_KEY, value.toString())
}
