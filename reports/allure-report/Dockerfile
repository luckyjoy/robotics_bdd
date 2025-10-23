FROM nginx:stable-alpine
LABEL maintainer="CI Pipeline"
ENV REPORT_BUILD_NUMBER=5
# Copy the static HTML report files (the Allure report) into the Nginx web root
COPY . /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
