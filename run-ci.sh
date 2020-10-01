echo "Linting ..." &&
flake8 --config=flake8-config.ini &&
echo "Testing ..." &&
pytest &&
echo "Reporting ..."
allure generate test-results --clean
echo "Done."