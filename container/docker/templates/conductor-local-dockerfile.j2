FROM {{ conductor_base }}
{% set distro = original_base.split(':')[0] %}
{% if distro_version in ["wheezy", "precise", "trusty"] %}
  pip install --no-cache-dir -U pyopenssl ndg-httpsclient pyasn1 && \
{% endif %}
# The COPY here will break cache if the requirements or ansible.cfg has changed
COPY /build-src /_ansible/build
COPY /container-src /_ansible/container

{% if install_requirements %}
RUN {{ install_requirements }}
{% endif %}

VOLUME /usr
{% if distro in ["ubuntu", "debian", "alpine"] %}
VOLUME /lib
{% endif %}


